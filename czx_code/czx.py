import csv
# out=open("czx50Wcsv",'wb')
# csv_write = csv_write(out,dialect='excel')
# path = 'C:\Users\chenz\Desktop\czx50W.csv'
with open(r'C:\Users\chenz\Desktop\Gatling_test\czxtest.csv', 'a',newline="") as fp:
    # writer = csv.writer(fp)
    # i=1000444449
    # while i<=1000500004:
    #     writer.writerow([hex(i)])
    #     i=i+1
    writer = csv.writer(fp)
    i=1
    while i<=25000:
        writer.writerow(["sdnid"+ str(i)])
        i=i+1