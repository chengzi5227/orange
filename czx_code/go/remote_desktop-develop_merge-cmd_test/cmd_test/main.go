package main

import (
	"cmd_test/client"
	"flag"
	"fmt"
	"math/rand"
	"strconv"
	"sync"
	"sync/atomic"
	"time"

	"github.com/go-ini/ini"
)

const (
	NetError         uint32 = 0
	TokenError       uint32 = 1
	DeviceCodeRepeat uint32 = 2
	TestFinish       uint32 = 3
)

// Avica 配置
// Websocket 服务器
var avica_ws_server = "ws-pre.avica.link"

// SSO 服务器
var avica_sso_server = "sso-pre.avica.link"

// API 服务器
var avica_api_server = "pre.avica.link"

// 账号
var avica_account = "vicli@rayvision.com"

// 密码
var avica_password = "Abc123456"

/////////////////

// RayLink 配置
// Websocket 服务器
var raylink_ws_server = "ws-pre.raylink.live"

// SSO 服务器
var raylink_sso_server = "sso-pre.renderbus.com"

// API 服务器
var raylink_api_server = "pre.raylink.live"

// 账号
var raylink_account = "18825267706"

// 密码
var raylink_password = "Abc123456"

// 账号前缀
var raylink_number = 11110000000

/////////////////

func make_id() (string, string) {
	id := strconv.Itoa(rand.Intn(9) + 1)
	var mac string
	for i := 0; i < 8; i++ {
		id = id + strconv.Itoa(rand.Intn(10))
	}
	for i := 0; i < 6; i++ {
		if i > 0 {
			mac = mac + "-"
		}
		mac = mac + strconv.Itoa(rand.Intn(10)) + strconv.Itoa(rand.Intn(10))
	}
	return id, mac
}

func main() {
	fmt.Println("running...")
	max_count := flag.Int("max", 1, "最大连接数")
	sleep_ms := flag.Int("sleep", 0, "每次连接间隔时长")
	retry := flag.Bool("retry", true, "连接断开后是否自动重连")
	list_delay := flag.Int("list", 0, "是否定时请求设备列表 0=不请求   >0 间隔指定秒数请求一次")
	rand_delay := flag.Bool("rand", true, "随机时间内请求设备列表   list ± 30")
	avica := flag.Bool("avica", false, "连接Avica环境，否则连接RayLink")
	login := flag.Bool("login", false, "是否登录账号")
	remove := flag.Bool("remove", false, "删除所有设备")
	load_token := flag.Bool("load_token", true, "使用上次登录成功时的Token，仅指定login选项时生效")
	flush_token := flag.Bool("flush_token", false, "是否在登录后刷新Token，仅指定login选项时生效")
	test_qps := flag.Bool("test_qps", false, "测试qps")
	check_token := flag.Bool("check_token", true, "连接后是否检查token（Get user info）")
	flag.Parse()

	var locker sync.Mutex
	var count int32
	var failed int32
	var qps int64
	rand.Seed(time.Now().UnixNano())
	cfg, err := ini.Load("config.ini")
	if err != nil {
		fmt.Println("Read config error:", err)
		cfg = ini.Empty()
	}
	for i := 0; i < *max_count; i++ {
		var id string
		var mac string
		var token string
		var account string
		var password string
		sec, err := cfg.GetSection(strconv.Itoa(i))
		if err == nil {
			key, err := sec.GetKey("id")
			if err == nil {
				id = key.String()
			}
			key, err = sec.GetKey("mac")
			if err == nil {
				mac = key.String()
			}
			key, err = sec.GetKey("token")
			if err == nil {
				token = key.String()
			}
		}

		if len(id) == 0 || len(mac) == 0 {
			id, mac = make_id()
			sec, err := cfg.NewSection(strconv.Itoa(i))
			if err == nil {
				sec.NewKey("id", id)
				sec.NewKey("mac", mac)
			}
		}
		if *login {
			account = strconv.Itoa(raylink_number + i%10000)
			password = account
			//account = raylink_account
			//password = raylink_password
		}
		//mac = "00-00-00-00-00-00"
		//fmt.Println("id:" + id)
		//fmt.Println("mac:" + mac)
		go func(i int, id string, mac string, token string, account string, password string) {
			for {
				if !*test_qps {
					fmt.Println("[" + strconv.Itoa(i) + "]Register id: " + id)
				}
				atomic.AddInt32(&count, 1)
				if *login {
					if !*load_token {
						token = ""
					}
					if len(token) == 0 {
						if *avica {
							d := client.Client{}
							token = d.Login(avica_api_server, avica_ws_server, avica_account, avica_password, "", "go client", mac, true)
						} else {
							d := client.Client{}
							token = d.Login(raylink_api_server, raylink_sso_server, account, password, "", "go client", mac, false)
						}
					}
					// 测试qps时不写磁盘，避免因为磁盘原因导致测试不准确
					if !*test_qps && len(token) > 0 {
						locker.Lock()
						cfg.Section(strconv.Itoa(i)).Key("token").SetValue(token)
						cfg.SaveTo("config.ini")
						locker.Unlock()
					}
				} else {
					token = ""
				}
				if !*login || len(token) > 0 {
					c := client.Client{}
					delay := *list_delay
					if delay > 0 && *rand_delay {
						delay = delay + rand.Intn(60) - 30
						if delay < 0 {
							delay = 1
						}
					}
					//fmt.Println(delay)
					var code uint32
					if *avica {
						code = c.Start(avica_api_server, avica_ws_server, token, id, "go client", mac, int32(delay), true, *remove, *flush_token, *test_qps, *check_token)
					} else {
						code = c.Start(raylink_api_server, raylink_ws_server, token, id, "go client", mac, int32(delay), false, *remove, *flush_token, *test_qps, *check_token)
					}
					if code == DeviceCodeRepeat {
						locker.Lock()
						id, mac = make_id()
						cfg.Section(strconv.Itoa(i)).Key("id").SetValue(id)
						cfg.Section(strconv.Itoa(i)).Key("mac").SetValue(mac)
						cfg.SaveTo("config.ini")
						locker.Unlock()
					} else if code == TokenError {
						fmt.Println("Clear token")
						token = ""
					} else if code == TestFinish {
						atomic.AddInt64(&qps, 1)
					}
				}

				atomic.AddInt32(&count, -1)
				if !*test_qps {
					fmt.Println("Unregister id: " + id)
				}
				atomic.AddInt32(&failed, 1)
				if !*retry {
					break
				}
			}

		}(i, id, mac, token, account, password)
		if *remove {
			break
		}
		if *sleep_ms > 0 {
			time.Sleep(time.Millisecond * time.Duration(*sleep_ms))
		}
	}
	locker.Lock()
	cfg.SaveTo("config.ini")
	locker.Unlock()
	var last_qps int64
	for {
		if !*test_qps {
			fmt.Println("Current online: " + strconv.Itoa(int(count)) + "   Failed(total): " + strconv.Itoa(int(failed)))
			time.Sleep(time.Second * 10)
		} else {
			tmp := qps
			fmt.Println("QPS: " + strconv.Itoa(int(tmp-last_qps)) + "/s")
			last_qps = tmp
			time.Sleep(time.Second * 1)
		}

	}
}
