from django.core.management import call_command

def schedule_db_backup():
    try:
        call_command('dbbackup')
    except:
        pass