taiko_rpc = "https://taiko.drpc.org"
sleep_between_accounts = (10, 20)
shuffle_accounts = True
mobile_proxy = "socks5://log:pass@ip:port"
change_ip_url = ""  # leave empty, if you have travchis

deposit_from_source_chains = False  # если нет баланса на taiko, скрипт будет депозитить баланс из source_chains
bridges_to_use = ["orbiter", "xy"]  # orbiter, xy
deposit_to_taiko_amount = (0.0003, 0.0004)
gas_multiplier = 2
