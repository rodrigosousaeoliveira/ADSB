#!/bin/bash

# Função para executar com prefixo
run_with_prefix() {
    local name=$1
    local color=$2
    local command=$3
    
    # Cores ANSI
    local RESET="\033[0m"
    case $color in
        red)    COLOR="\033[31m" ;;
        green)  COLOR="\033[32m" ;;
        yellow) COLOR="\033[33m" ;;
        blue)   COLOR="\033[34m" ;;
        purple) COLOR="\033[35m" ;;
        cyan)   COLOR="\033[36m" ;;
        *)      COLOR="\033[37m" ;;
    esac
    
    # Executar com prefixo
    eval "$command" | while IFS= read -r line; do
        printf "${COLOR}[%s]${RESET} %s\n" "$name" "$line"
    done
}

cleanup() {
    echo "Parando todos os processos..."
    pkill -P $$
    exit 0
}

trap cleanup SIGINT SIGTERM

source venv/bin/activate
# Executar scripts
run_with_prefix "PROC1" "green" "create_ap wlan0 end0 ADSBlive --no-virt" &
PID1=$!

run_with_prefix "PROC2" "yellow" "python server.py" &
PID2=$!

run_with_prefix "PROC3" "blue" "python readtofile.py" &
PID3=$!

wait
