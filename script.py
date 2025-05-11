import xbmcgui
import subprocess

def get_bars(bars):
    if bars > 80:
        return "[*****]"
    if bars > 60:
        return "[**** ]"
    if bars > 40:
        return "[***  ]"
    if bars > 20:
        return "[**   ]"
    return "[*     ]"

dialog = xbmcgui.Dialog()

yesno = dialog.yesno("NetworkManager", "Do you want to scan the available Wi-Fi networks?", "Cancel", "Scan")

if(yesno):
    output = subprocess.check_output(['nmcli', '-t', '-f', 'SSID,RATE,SIGNAL,ACTIVE,BSSID' ,'d', 'wifi' ,'list'], universal_newlines=True)
    networks = output.strip().split('\n')
    formatted_ssids = []
    formatted_bssids = []
    for network in networks:
        hidden_network_prefix = ''
        if network[0] == ':':
            hidden_network_prefix += 'Unnamed network '
        parsed_network = network.replace("\\", "")
        bssid_arr = parsed_network.split(':')[-6:]
        bssid = ':'.join(bssid_arr)
        formatted_bssids.append(bssid)
        without_bssid = parsed_network.split(':' + bssid)[0]
        network_info_arr = without_bssid.split(':')
        active_status = ' [Connected]' if network_info_arr[-1] == 'yes' else ''
        signal_bars = int(network_info_arr[-2])
        bars_in_asterisk = get_bars(signal_bars)
        full_network_name = hidden_network_prefix + ' '.join(network_info_arr[:-2]) + ' ' + bars_in_asterisk + active_status
        formatted_ssids.append(xbmcgui.ListItem(full_network_name, network_info_arr[0] if len(hidden_network_prefix) == 0 else hidden_network_prefix))

    selected_network_int = dialog.select('Select the network', formatted_ssids)
    if selected_network_int < 0:
        quit()
    selected_network_list_item = formatted_ssids[selected_network_int]
    selected_network_bssid = formatted_bssids[selected_network_int]
    if selected_network_list_item.getLabel().endswith('[Connected]'):
        res_discon = dialog.yesnocustom(heading=selected_network_list_item.getLabel2(), message='You are already connected to this network.', customlabel='Change password', nolabel='Cancel', yeslabel='Disconnect')
        if res_discon == 1:
            subprocess.run(['nmcli', 'connection', 'delete', selected_network_list_item.getLabel2()], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            dialog.notification('NetworkManager', 'Successfully disconnected from ' + selected_network_list_item.getLabel2() + '!')
            quit()
        if res_discon < 1:
            quit()
    password = dialog.input('Enter the password for ' + selected_network_list_item.getLabel2(), type=xbmcgui.INPUT_ALPHANUM, option=xbmcgui.ALPHANUM_HIDE_INPUT)
    if len(password) == 0:
        quit()
    subprocess.run(['nmcli', 'connection', 'delete', selected_network_list_item.getLabel2()])
    res_conn = subprocess.run(['nmcli', 'device', 'wifi', 'connect', selected_network_bssid, 'password', password], capture_output=True)
    if res_conn.returncode == 0:
        dialog.notification('NetworkManager', selected_network_list_item.getLabel2() + ' connected successfully!')
    else:
        dialog.notification('NetworkManager', 'Wrong password!', xbmcgui.NOTIFICATION_ERROR)
