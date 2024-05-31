import requests
import pandas as pd
from colorama import init, Fore, Style
from tabulate import tabulate
import os
import time

init()

def read_wallets(file_path):
    with open(file_path, 'r') as file:
        wallets = file.read().splitlines()
    return wallets

def process_response(wallet, response):
    eligible_projects = [project['project'] for project in response if project.get('isEligible')]
    if not eligible_projects:
        print(f"Кошелек {Fore.RED}{wallet}{Style.RESET_ALL} не eligible\n")
    return eligible_projects

def check_wallets(file_path):
    wallets = read_wallets(file_path)
    wallet_project_map = {}

    for wallet in wallets:
        wallet = wallet.strip()
        url = f"https://wenser.vercel.app/api/layerzerorfp?address={wallet}"
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            eligible_projects = process_response(wallet, data)
            wallet_project_map[wallet] = eligible_projects
            time.sleep(1)
        except requests.exceptions.RequestException as e:
            print(f"Ошибка запроса для кошелька {wallet}: {e}")
        except ValueError:
            print(f"Ошибка декодирования JSON для кошелька {wallet}")

    results = []
    for i, (wallet, projects) in enumerate(wallet_project_map.items(), 1):
        if projects:
            print(f"{i}.{Fore.GREEN}{wallet}{Style.RESET_ALL}")
            print("RFP:")
            table = [[project] for project in projects]
            print(tabulate(table, tablefmt="grid"))
            print(f"Кошелек {Fore.GREEN + Style.BRIGHT}eligible{Style.RESET_ALL} по {Fore.BLUE + Style.BRIGHT}{len(projects)} RFP{Style.RESET_ALL}\n")
            results.append({
                'Wallet': wallet,
                'Eligible RFPs': len(projects),
                'Projects': ', '.join(projects)
            })

    os.makedirs('results', exist_ok=True)
    
    df = pd.DataFrame(results)
    df.to_csv('results/wallet.csv', index=False)
    df.to_excel('results/wallet.xlsx', index=False)

if __name__ == "__main__":
    file_path = 'wallet.txt'
    check_wallets(file_path)
