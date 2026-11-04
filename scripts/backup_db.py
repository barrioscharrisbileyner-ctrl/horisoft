import argparse
import subprocess
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description='Export the Docker Compose MySQL database.')
    parser.add_argument('destination', type=Path, help='Destination SQL file')
    args = parser.parse_args()
    args.destination.parent.mkdir(parents=True, exist_ok=True)
    temporary_path = args.destination.with_suffix(args.destination.suffix + '.tmp')

    command = [
        'docker', 'compose', 'exec', '-T', 'db', 'sh', '-c',
        'MYSQL_PWD="$MYSQL_ROOT_PASSWORD" exec mysqldump -uroot "$MYSQL_DATABASE" --single-transaction --routines --triggers',
    ]
    with temporary_path.open('wb') as backup:
        result = subprocess.run(command, stdout=backup, check=False)
    if result.returncode:
        temporary_path.unlink(missing_ok=True)
        raise SystemExit(result.returncode)
    temporary_path.replace(args.destination)
    print(f'Database backup written to {args.destination}')


if __name__ == '__main__':
    main()
