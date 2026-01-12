#!/bin/bash


#***********************************************************************
# function rm-on-exit() -> deleting temporary files on exit
#-----------------------------------------------------------------------
declare -a files_to_be_deleted

function rm-on-exit() {
	[[ $# -gt 0 ]] && files_to_be_deleted+=("$@")
}

function on-exit() {
	for file in "${files_to_be_deleted[@]:-}"; do
		[[ -f "$file" ]] && rm -r "$file"
	done
	files_to_be_deleted=()
}

trap on-exit EXIT INT TERM QUIT ABRT ERR
#***********************************************************************


#***********************************************************************
after_rules="$HOME/222/file-test-origin.txt"
after_rules_tmp="$HOME/222/file-test-tmp.txt"
after_rules_result="$HOME/222/file-test-result.txt"

function container--file() {
	cp "$after_rules" "$after_rules_tmp"  # create temp file
	rm-on-exit "$after_rules_tmp"         # delete temp file

	#********************************************** delete OLD
	sed "/^BEGIN start/,/^END stop/d" "$after_rules" > "$after_rules_tmp"

	#********************************************** added block text
	>> "${after_rules_tmp}" cat <<-\EOF
	BEGIN start
	new first string
	new second string
	END stop
	EOF
	#********************************************** "EOF" end of block of text

	diff -u --color=auto "$after_rules" "$after_rules_tmp"
	cat "$after_rules_tmp" > "$after_rules_result"
}
#***********************************************************************


#***********************************************************************
function container--start() {
	declare service_action="${1:-help}"
	case "$service_action" in
	start)
		execute_command "docker stop redis_new"
		;;
	*)
		execute_command "docker stop pgadmin_new"
		;;
esac
}
#*****************************************************************
#*******************************************************************
#********************************************************************
#*********************************************************************
#**********************************************************************
#***********************************************************************







#***********************************************************************
# Функция для выполнения команды с выводом результата
#-----------------------------------------------------------------------
execute_command() {
    local command="$1"
    echo "--------------------------------------------------"
    echo "$>  $command"
    eval "$command"
    local exit_code=$?
    if [ $exit_code -eq 0 ]; then
        echo "--------------------------------------------------"
    else
        echo "Command failed with exit code $exit_code"
    fi
    echo
}
#***********************************************************************


#***********************************************************************
# stopping all containers on the network -> 172.20.0.0/16
#-----------------------------------------------------------------------
function container--stop() {
  execute_command "docker stop nginx_new"
  execute_command "docker stop celery_two_new"
  execute_command "docker stop app_first_new"
  execute_command "docker stop app_two_new"
  execute_command "docker stop celery_worker_new"

  execute_command "docker stop pgadmin_new"
  execute_command "docker stop redis_new"
  execute_command "docker stop postgresql_db_new"

  execute_command "docker stop flower_new_two"
  execute_command "docker stop flower_new_first"
}
#***********************************************************************


#***********************************************************************
# docker network create -> 172.20.0.0/16
#-----------------------------------------------------------------------
function network--create() {
  execute_command "docker network create -d bridge --subnet=172.20.0.0/16 --ip-range=172.20.0.0/16 --gateway=172.20.0.1 app_net_new"
}
#***********************************************************************


#***********************************************************************
# output of hints about commands
#-----------------------------------------------------------------------
function cmd--help() {
	cat <<-EOF >&2
	  cmd net-create --> docker network create "172.20.0.0/16"
	  cmd cont-stop  --> docker stop "all"
	EOF
}
#***********************************************************************




#***********************************************************************
#***********************************************************************
#     __main__
#-----------------------------------------------------------------------
#***********************************************************************
cmd_action="${1:-}"

case "$cmd_action" in
  net-create)
		network--create
		;;
  cont-stop)
		container--stop
		;;
	start)
		container--start "$@"
		;;
  file)
		container--file
		;;
	*)
		cmd--help
		;;
esac
#***********************************************************************
#***********************************************************************
