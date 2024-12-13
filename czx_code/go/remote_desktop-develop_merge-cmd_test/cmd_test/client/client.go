package client

import (
	"bytes"
	"cmd_test/common"
	"cmd_test/remote_desktop"
	"crypto/aes"
	"crypto/cipher"
	"crypto/sha1"
	"encoding/base64"
	"encoding/hex"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"time"

	"github.com/gorilla/websocket"
	"google.golang.org/protobuf/proto"
)

var avica_biz string = "678"
var avica_accessId string = "fERTA0lRzOEYZVPUkHmkO9x"
var raylink_biz string = "888"
var raylink_accessId string = "QHLZV6eQ9cpkSA7n8ighRZu"
var clientVersion string = "8.8.8.8"
var osVersion string = "Windows 10 LTS"

const (
	NetError         uint32 = 0
	TokenError       uint32 = 1
	DeviceCodeRepeat uint32 = 2
	TestFinish       uint32 = 3
)

type Client struct {
	msgId      int32
	deviceCode string
	deviceName string
	macAddress string
	list_sleep int32
	last_heart int32
	avica      bool
	remove     bool
	test_qps   bool
	msg        chan []byte
	ret_code   chan uint32
}

type generateCode_Data struct {
	Generate string `json:"generate"`
}

type generateCode struct {
	Result bool              `json:"result"`
	Data   generateCode_Data `json:"data"`
}

type extendData struct {
	Zone int32 `json:"zone"`
}

type loginRequest struct {
	LoginName     string     `json:"loginName"`
	Password      string     `json:"password"`
	LoginPlatform int32      `json:"loginPlatform"`
	Randstr       string     `json:"randstr"`
	SliderType    int32      `json:"sliderType"`
	Customer      string     `json:"customer"`
	ClientVersion string     `json:"clientVersion"`
	OsVersion     string     `json:"osVersion"`
	DeviceCode    string     `json:"deviceCode"`
	DeviceName    string     `json:"deviceName"`
	MacAddress    string     `json:"macAddress"`
	LoginOS       int32      `json:"loginOs"`
	ExtendData    extendData `json:"extendData"`
}

type loginResponse_Data struct {
	Token string `json:"rsAuthToken"`
}

type loginResponse struct {
	Result  bool               `json:"result"`
	Data    loginResponse_Data `json:"data"`
	Message string             `json:"message"`
}

type getUserInfoResponse struct {
	Result  bool   `json:"result"`
	Code    int32  `json:"code"`
	Message string `json:"message"`
}

type flushTokenRequest struct {
	UserKey       string `json:"userKey"`
	LoginPlatform int32  `json:"loginPlatform"`
}

type flushTokenResponse struct {
	Code int32 `json:"code"`
}

func (thiz *Client) Login(api_host string, sso_host string, accout string, password string, deviceCode string, deviceName string, macAddress string, avica bool) string {
	thiz.deviceCode = deviceCode
	thiz.macAddress = macAddress
	thiz.deviceName = deviceName
	thiz.avica = avica

	var token string
	if len(accout) > 0 && len(password) > 0 {
		code := thiz.getRamdomCode("https://"+sso_host, accout)
		if code == "" {
			return ""
		}
		//fmt.Println(code)
		token = thiz.login("https://"+api_host, accout, password, code)
		//fmt.Println(string(token))
		if len(token) == 0 {
			return ""
		}
	}
	return token
}

func (thiz *Client) Start(api_host string, wss_host string, token string, deviceCode string, deviceName string, macAddress string, list_sleep int32, avica bool, remove bool, flush_token bool, test_qps bool, check_token bool) uint32 {
	thiz.deviceCode = deviceCode
	thiz.macAddress = macAddress
	thiz.deviceName = deviceName
	thiz.list_sleep = list_sleep
	thiz.avica = avica
	thiz.remove = remove
	thiz.test_qps = test_qps

	defer func() {
		if err := recover(); err != nil {
			fmt.Println(err)
		}
	}()

	//token = "rsat:2fDSJtaa7V1eh0JhuAxgAG5zFNt"
	var c *websocket.Conn
	var err error
	if len(token) > 0 {
		if check_token && !thiz.getUserInfo(api_host, token) {
			return TokenError
		}
		if flush_token && !thiz.flushToken(api_host, token) {
			return TokenError
		}
		if avica {
			c, _, err = websocket.DefaultDialer.Dial("wss://"+api_host+"/ws?token="+token+"&deviceCode="+thiz.deviceCode+"&area=2", nil)
		} else {
			c, _, err = websocket.DefaultDialer.Dial("wss://"+api_host+"/ws?token="+token+"&deviceCode="+thiz.deviceCode+"&area=1", nil)
		}

		if err != nil {
			fmt.Println("Create websocket error:", err)
			return NetError
		}
	} else {
		c, _, err = websocket.DefaultDialer.Dial("wss://"+api_host+"/ws", nil)
		if err != nil {
			fmt.Println("Create websocket error:", err)
			return NetError
		}
	}
	defer c.Close()

	thiz.msg = make(chan []byte)
	thiz.ret_code = make(chan uint32)

	done := make(chan struct{})
	go func() {
		defer close(done)
		for {
			_, message, err := c.ReadMessage()
			if err != nil {
				fmt.Println("Read websocket data error:", err)
				return
			}
			if !thiz.handleMessage(c, message) {
				return
			}
		}
	}()

	// send check message
	go thiz.sendCheckRequest(c)

	ticker := time.NewTicker(time.Second * 1)
	defer ticker.Stop()

	thiz.last_heart = int32(time.Now().Second())
	heart := 0
	list := 0
	run := true
	var ret uint32
	for run {
		select {
		case <-done:
			run = false
		case msg := <-thiz.msg:
			err = c.WriteMessage(websocket.BinaryMessage, msg)
			if err != nil {
				fmt.Println("Send data error:", err)
				run = false
			}
		case code := <-thiz.ret_code:
			ret = code
		case <-ticker.C:
			// 检查是否长时间未收到心跳消息
			if int32(time.Now().Second())-thiz.last_heart > 30 {
				fmt.Println("Websocket time out.")
				run = false
				break
			}
			heart = heart + 1
			if heart%10 == 0 {
				//fmt.Println("heart")
				request := &remote_desktop.Heart{}
				thiz.msgId = thiz.msgId + 1
				request.MessageId = thiz.msgId
				req, _ := proto.Marshal(request)
				data := make([]byte, 1)
				data[0] = byte(remote_desktop.MessageType_msg_heart)
				data = append(data, req...)
				//fmt.Println(data)
				//fmt.Println("client heart.")
				err = c.WriteMessage(websocket.BinaryMessage, data)
				if err != nil {
					fmt.Println("Send data error:", err)
					run = false
					break
				}
			}
			list = list + 1
			if thiz.remove || (thiz.list_sleep > 0 && list%int(thiz.list_sleep) == 0) {
				thiz.sendDeviceList(c)
			}
		}
	}
	return ret
}

func (thiz *Client) handleMessage(c *websocket.Conn, message []byte) bool {
	if len(message) == 0 {
		return false
	}
	switch message[0] {
	case byte(remote_desktop.MessageType_msg_heart):
		response := &remote_desktop.Heart{}
		err := proto.Unmarshal(message[1:], response)
		if err != nil {
			fmt.Println("Protocol error:", err)
			return false
		}
		//fmt.Println("server heart.")
		thiz.last_heart = int32(time.Now().Second())

	case byte(remote_desktop.MessageType_msg_check_response):
		response := &remote_desktop.CheckResponse{}
		err := proto.Unmarshal(message[1:], response)
		if err != nil {
			fmt.Println("Protocol error:", err)
			return false
		}
		//fmt.Println("check response.")
		if response.Error == common.ErrorCode_success || response.Error == common.ErrorCode_version_too_low_no_force {
			//fmt.Println("success")
			thiz.sendDnsDomain(c)
		} else {
			fmt.Println("check failed", response.Error)
			return false
		}

	case byte(remote_desktop.MessageType_msg_get_dns_domain_response):
		response := &remote_desktop.GetDnsDomainResponse{}
		err := proto.Unmarshal(message[1:], response)
		if err != nil {
			fmt.Println("Protocol error:", err)
			return false
		}
		//fmt.Println("dns response.")
		if response.Error == common.ErrorCode_success {
			//fmt.Println("success")
			thiz.sendRootInfo(c)
		} else {
			fmt.Println("get dns domain failed")
			return false
		}

	case byte(remote_desktop.MessageType_msg_get_sdn_root_info_response):
		response := &remote_desktop.GetSdnRootInfoResponse{}
		err := proto.Unmarshal(message[1:], response)
		if err != nil {
			fmt.Println("Protocol error:", err)
			return false
		}
		//fmt.Println("root info response.")
		thiz.sendRegisterId(c)

	case byte(remote_desktop.MessageType_msg_register_id_response):
		response := &remote_desktop.RegisterIdResponse{}
		err := proto.Unmarshal(message[1:], response)
		if err != nil {
			fmt.Println("Protocol error:", err)
			return false
		}
		//fmt.Println("register id response.")
		if response.Error == common.ErrorCode_success {
			//fmt.Println("success")
			if thiz.test_qps {
				thiz.ret_code <- TestFinish
				return false
			}
		} else {
			fmt.Println("register id failed")
			thiz.ret_code <- DeviceCodeRepeat
			return false
		}

	case byte(remote_desktop.MessageType_msg_get_device_list_response):
		response := &remote_desktop.GetDeviceListResponse{}
		err := proto.Unmarshal(message[1:], response)
		if err != nil {
			fmt.Println("Protocol error:", err)
			return false
		}
		//fmt.Println("register id response.")
		if response.Error == common.ErrorCode_success {
			//fmt.Println("success")
			if thiz.remove {
				fmt.Println("remove all device list")
			}
			for i := range response.DeviceList {
				fmt.Println("remove:", response.DeviceList[i].NodeId)
				thiz.sendRemoveDeviceList(c, response.DeviceList[i].NodeId)
			}
		} else {
			fmt.Println("get device list failed", response.Error)
			return false
		}

	case byte(remote_desktop.MessageType_msg_delete_device_response):
		response := &remote_desktop.DeleteDeviceResponse{}
		err := proto.Unmarshal(message[1:], response)
		if err != nil {
			fmt.Println("Protocol error:", err)
			return false
		}
		//fmt.Println("register id response.")
		if response.Error == common.ErrorCode_success {
			//fmt.Println("success")
		} else {
			fmt.Println("remove device failed", response.Error)
			return false
		}
	}
	return true
}

func (thiz *Client) login(host string, accout string, password string, randstr string) string {
	request := &loginRequest{}
	request.LoginName = accout
	request.Password = encryptPassword(password)
	request.LoginPlatform = 1
	request.Randstr = randstr
	request.SliderType = 0
	request.Customer = accout
	request.ClientVersion = clientVersion
	request.OsVersion = osVersion
	request.DeviceCode = thiz.deviceCode
	request.DeviceName = thiz.deviceName
	request.MacAddress = thiz.macAddress
	request.LoginOS = 0         // Windows
	request.ExtendData.Zone = 2 // 1 = 国内   2 = 国外
	str, err := json.Marshal(request)
	if err != nil {
		return ""
	}
	//fmt.Println(string(str))
	client := &http.Client{}
	req, err := http.NewRequest("POST", host+"/api/user/login/signIn", bytes.NewBuffer(str))
	if err != nil {
		fmt.Println("Make login request error:", err)
		return ""
	}
	req.Header.Add("Content-Type", "application/json")
	resp, err := client.Do(req)
	if err != nil {
		fmt.Println("Send login request error:", err)
		return ""
	}
	defer resp.Body.Close()
	body, err := io.ReadAll(resp.Body)
	response := &loginResponse{}
	err = json.Unmarshal(body, response)
	if err != nil {
		fmt.Println("[Login]Unmarshal json error:", resp.StatusCode, err, string(body))
		return ""
	}
	if !response.Result {
		fmt.Println("Login error:", response.Message)
		return ""
	}
	//fmt.Println(string(body))
	return response.Data.Token
}

func (thiz *Client) getUserInfo(host string, token string) bool {
	client := &http.Client{}
	var uri string
	if thiz.avica {
		uri = "https://" + host + "/api/user/customer/getUserInfo?rsAuthToken=" + token + "&area=2"
	} else {
		uri = "https://" + host + "/api/user/customer/getUserInfo?rsAuthToken=" + token
	}
	req, err := http.NewRequest("GET", uri, nil)
	if err != nil {
		fmt.Println("Make user info request error:", err)
		return false
	}
	req.Header.Add("userKey", token)
	req.Header.Add("Content-Type", "application/json")
	resp, err := client.Do(req)
	if err != nil {
		fmt.Println("Send user info request error:", err)
		return false
	}
	defer resp.Body.Close()
	body, err := io.ReadAll(resp.Body)
	//fmt.Println(string(body))
	response := &getUserInfoResponse{}
	err = json.Unmarshal(body, response)
	if err != nil {
		fmt.Println("[Get user info]Unmarshal json error:", resp.StatusCode, err, string(body))
		return false
	}
	if !response.Result || response.Code != 200 {
		fmt.Println("Get user info error:", response.Message)
		return false
	}

	return true
}

func (thiz *Client) flushToken(host string, token string) bool {
	request := &flushTokenRequest{}
	request.UserKey = token
	request.LoginPlatform = 1
	str, err := json.Marshal(request)
	if err != nil {
		return false
	}

	client := &http.Client{}
	req, err := http.NewRequest("POST", "https://"+host+"/api/user/login/flushTokenExpireTime", bytes.NewBuffer(str))
	if err != nil {
		fmt.Println("Make flush request error:", err)
		return false
	}
	req.Header.Add("userKey", token)
	req.Header.Add("Content-Type", "application/json")
	resp, err := client.Do(req)
	if err != nil {
		fmt.Println("Send flush request error:", err)
		return false
	}
	defer resp.Body.Close()
	body, err := io.ReadAll(resp.Body)
	response := &flushTokenResponse{}
	err = json.Unmarshal(body, response)
	if err != nil {
		fmt.Println("[Flush token]Unmarshal json error:", resp.StatusCode, err, string(body))
		return false
	}
	if response.Code != 200 {
		fmt.Println("Flush error:", string(body))
		return false
	}

	return true
}

func (thiz *Client) sendCheckRequest(c *websocket.Conn) {
	//fmt.Println("send check request.")
	request := &remote_desktop.Check{}
	thiz.msgId = thiz.msgId + 1
	request.MessageId = thiz.msgId
	request.Platform = common.PlatformType_windows
	request.Version = 8888
	data := make([]byte, 1)
	data[0] = byte(remote_desktop.MessageType_msg_check)
	req, _ := proto.Marshal(request)
	data = append(data, req...)
	thiz.msg <- data
}

func (thiz *Client) sendDnsDomain(c *websocket.Conn) {
	//fmt.Println("send domain request.")
	request := &remote_desktop.GetDnsDomain{}
	thiz.msgId = thiz.msgId + 1
	request.MessageId = thiz.msgId
	data := make([]byte, 1)
	data[0] = byte(remote_desktop.MessageType_msg_get_dns_domain)
	req, _ := proto.Marshal(request)
	data = append(data, req...)
	thiz.msg <- data
}

func (thiz *Client) sendRootInfo(c *websocket.Conn) {
	//fmt.Println("send root info request.")
	request := &remote_desktop.GetSdnRootInfo{}
	thiz.msgId = thiz.msgId + 1
	request.MessageId = thiz.msgId
	request.Index = 0
	data := make([]byte, 1)
	data[0] = byte(remote_desktop.MessageType_msg_get_sdn_root_info)
	req, _ := proto.Marshal(request)
	data = append(data, req...)
	thiz.msg <- data
}

func (thiz *Client) sendRegisterId(c *websocket.Conn) {
	//fmt.Println("send register id request.")
	request := &remote_desktop.RegisterId{}
	thiz.msgId = thiz.msgId + 1
	request.MessageId = thiz.msgId
	request.DeviceId = []byte(thiz.deviceCode)
	request.MacAddr = []byte(thiz.macAddress)
	request.Platform = common.PlatformType_windows
	request.MachineName = []byte(thiz.deviceName)
	request.SystemVersion = []byte(osVersion)
	request.NatBehavior = 4
	request.Version = []byte(clientVersion)
	data := make([]byte, 1)
	data[0] = byte(remote_desktop.MessageType_msg_register_id)
	req, _ := proto.Marshal(request)
	data = append(data, req...)
	thiz.msg <- data
}

func (thiz *Client) sendDeviceList(c *websocket.Conn) {
	//fmt.Println("send device list request.")
	request := &remote_desktop.GetDeviceList{}
	thiz.msgId = thiz.msgId + 1
	request.MessageId = thiz.msgId
	request.GroupId = 0
	data := make([]byte, 1)
	data[0] = byte(remote_desktop.MessageType_msg_get_device_list)
	req, _ := proto.Marshal(request)
	data = append(data, req...)
	thiz.msg <- data
}

func (thiz *Client) sendRemoveDeviceList(c *websocket.Conn, nodeId int32) {
	//fmt.Println("send device list request.")
	request := &remote_desktop.DeleteDevice{}
	thiz.msgId = thiz.msgId + 1
	request.MessageId = thiz.msgId
	request.NodeId = nodeId
	data := make([]byte, 1)
	data[0] = byte(remote_desktop.MessageType_msg_delete_device)
	req, _ := proto.Marshal(request)
	data = append(data, req...)
	thiz.msg <- data
}

func encryptPassword(password string) string {
	SALT := []string{"vaBci", "l6AF8", "vM9vH"}
	split_len := len(password) / len(SALT)
	var output string
	for i := 0; i < len(SALT)-1; i++ {
		output = output + string([]byte(password)[i*split_len:(i+1)*split_len]) + SALT[i]
	}
	output = output + string([]byte(password)[(len(SALT)-1)*split_len:]) + SALT[len(SALT)-1]
	//fmt.Println(output)
	hash := sha1.New()
	hash.Write([]byte(output))
	return hex.EncodeToString(hash.Sum(nil))
}

func (thiz *Client) getRamdomCode(host string, accout string) string {
	client := &http.Client{}
	req, err := http.NewRequest("GET", host+"/api/sso/verify/sendGenerateCode", nil)
	if err != nil {
		fmt.Println("Make ramdom request error:", err)
		return ""
	}
	req.Header.Add("phone", accout)
	req.Header.Add("macAddress", thiz.macAddress)
	req.Header.Add("Content-Type", "application/json")
	if thiz.avica {
		req.Header.Add("biz", avica_biz)
		req.Header.Add("accessId", avica_accessId)
	} else {
		req.Header.Add("biz", raylink_biz)
		req.Header.Add("accessId", raylink_accessId)
	}

	resp, err := client.Do(req)
	if err != nil {
		fmt.Println("Send ramdom request error:", err)
		return ""
	}
	defer resp.Body.Close()
	body, err := io.ReadAll(resp.Body)
	//fmt.Println(string(body))
	get_code := &generateCode{}
	err = json.Unmarshal(body, get_code)
	if err != nil {
		fmt.Println("[Get code]Unmarshal json error:", resp.StatusCode, err, string(body))
		return ""
	}
	//fmt.Println(get_code.Data.Generate)
	return encryptCode([]byte(get_code.Data.Generate))
}

func pkcs5Padding(plaintext []byte, blockSize int) []byte {
	padding := blockSize - len(plaintext)%blockSize
	padtext := bytes.Repeat([]byte{byte(padding)}, padding)
	return append(plaintext, padtext...)
}

func encryptCode(data []byte) string {
	key := []byte("3e84437e664b070e644dd91da0b80088")
	block, err := aes.NewCipher(key)
	if err != nil {
		return ""
	}
	blockSize := block.BlockSize()
	data = pkcs5Padding(data, blockSize)
	blockMode := cipher.NewCBCEncrypter(block, key[:blockSize])
	crypted := make([]byte, len(data))
	blockMode.CryptBlocks(crypted, data)
	return base64.StdEncoding.EncodeToString(crypted)
}
