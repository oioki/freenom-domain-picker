#!/usr/bin/env python3

import argparse
import sys

import requests


BASE_URL = 'https://my.freenom.com/includes/domains/fn-available.php'
ATTEMPTS = 10

parser = argparse.ArgumentParser(description="Find free Freenom domains based on wordlist")
parser.add_argument('-w', '--wordlist', default='/dev/stdin', help="File with words to try")
parser.add_argument('-a', '--all', action='store_true', help="If true, show also non-free domains")
args = parser.parse_args()


def show_progress(current, total):
    progress = 100 * current / total
    sys.stdout.write('\r:: Progress: [{}/{} = {:.2f} %]'.format(current, total, progress))
    sys.stdout.flush()


def get_domain_data(domain):
    for attempt in range(ATTEMPTS):
        try:
            headers = {'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'}
            data = 'domain={}&tld='.format(domain)
            r = requests.post(BASE_URL, headers=headers, data=data, timeout=1)

            json_data = r.json()
            return json_data
        except Exception as e:
            if attempt == ATTEMPTS-1:
                print('\rError while checking `{}` domain: {}'.format(domain, str(e)))

    return None


def get_matching_domains(data):
    domains = []

    for candidate_domain in data['free_domains']:
        if candidate_domain['status'] == 'AVAILABLE':
            fqdn = candidate_domain['domain'] + candidate_domain['tld']
            if candidate_domain['type'] == 'FREE':
                price = 'free'
            else:
                price = '{}.{} {}'.format(candidate_domain['price_int'], candidate_domain['price_cent'], candidate_domain['currency'])
            domains.append({'fqdn': fqdn, 'price': price})

    return domains


def print_matching_domains(domains_data):
    sys.stdout.write("\r\033[K")
    for domain in domains_data:
        if domain['price'] == 'free':
            print(domain['fqdn'])
        elif args.all:
            print(domain['fqdn'], '--', domain['price'])


if __name__ == '__main__':
    with open(args.wordlist) as f:
        words = [s.rstrip() for s in f.readlines()]

        i = 0
        for word in words:
            i += 1
            show_progress(i, len(words))

            domain_data = get_domain_data(word)
            if not domain_data:
                continue

            domains_found = get_matching_domains(domain_data)
            if domains_found:
                print_matching_domains(domains_found)
