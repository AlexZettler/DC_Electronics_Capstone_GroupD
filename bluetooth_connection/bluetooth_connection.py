import bluetooth

print("performing inquiry...")


def get_device_ids():
    nearby_devices = bluetooth.discover_devices(
    duration=8, lookup_names=True, flush_cache=True, lookup_class=False)

    numn_devices = len(nearby_devices)
    print(f"found {numn_devices} devices")

    for addr, name in nearby_devices:
    
        #try:
        print(f"  {addr}, {name}")
        #except UnicodeEncodeError:
        #    print("  %s - %s" % (addr, name.encode('utf-8', 'replace')))


if __name__ == "__main__":
    get_device_ids()
