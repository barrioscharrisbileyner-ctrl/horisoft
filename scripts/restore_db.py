import argparse
import subprocess
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description='Restore a SQL backup into the Docker Compose database.')
    parser.add_argument('backup', type=Path, help='SQL backup file')
    parser.add_argument('--confirm-database', required=True, help='Type the exact database name to confirm overwrite')
    args = parser.parse_args()
    if not args.backup.is_file():
        parser.error(f'Backup file not found: {args.backup}')

    database_result = subprocess.run(
        ['docker', 'compose', 'exec', '-T', 'db', 'printenv', 'MYSQL_DATABASE'],
        check=True,
        capture_output=True,
        text=True,
    )
    target_database = database_result.stdout.strip()
    if args.confirm_database != target_database:
        parser.error(f'Confirmation must match the configured database: {target_database}')

    expected_confirmation = f'RESTORE-{args.confirm_database}'
    if input(f'This overwrites database {args.confirm_database}. Type {expected_confirmation}: ') != expected_confirmation:
        raise SystemExit('Restore cancelled.')

    command = [
        'docker', 'compose', 'exec', '-T', 'db', 'sh', '-c',
        'MYSQL_PWD="$MYSQL_ROOT_PASSWORD" exec mysql -uroot "$MYSQL_DATABASE"',
    ]
    with args.backup.open('rb') as backup:
        result = subprocess.run(command, stdin=backup, check=False)
    if result.returncode:
        raise SystemExit(result.returncode)
    print(f'Database restored from {args.backup}')


if __name__ == '__main__':
    main()
