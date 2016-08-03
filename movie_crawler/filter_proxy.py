#encoding:utf-8


def filter():
    ip_list, protocol_list, proxy_list = [], [], []
    with open('unfilter_proxy.txt', 'r') as f:
        for i, line in enumerate(f):
            sp = line.split('\t')
            if i % 2 == 0:
                ip_list.append(sp[1] + ':' + sp[2])
            if i % 2 == 1:
                protocol_list.append(sp[0].lower())
        for i in range(len(ip_list)):
            proxy_list.append(protocol_list[i] + '://' + ip_list[i])

    with open('proxy_list.txt', 'w') as f:
        for address in proxy_list:
            f.write(address + '\n')

if __name__ == '__main__':
    filter()
