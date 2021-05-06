# Homeload-TV downloader (Python)

This is a software which automatically downloads
of all files available for download from the download portal
[Homeload-TV](https://www.homeloadtv.com/).

## Requirements
The service was developed using Python 3.9.
It will probably work down to 3.7. It won't work with Python 2.

## Installation
Please us "venv" to execute this software:

```
git clone https://github.com/kettenbach-it/homeloadtv-downloader
cd homeloadtv-downloader
python3 -m venv venv --copies
source venv/bin/activate
cp hltvdlm.example.conf hltvdlm.conf
# edit hltvdlm.conf according to your needs
python3 hltvdlm.py
```

## Configuration
Place [hltvdlm.example.conf](hltvdlm.example.conf) either as hltvdlm.conf
in the directory with this software or as .hltvdlm.conf in the
home of the user running the software (.e.g. with cron).

```
[DEFAULT]
outputpath = /home/user/Downloads  # Directory you want the downloaded files stored to
username = user@domain.com  # Your username at homeloadtv.com 
password = XYZXYZYZY  # Your password at homeloadtv.com

```


## Usage
Run it with

```
python3 hltvdlm.py
```

or add it to crontab:

```
*/5 * * * * umask 0002; /usr/bin/python3 ~/homeloadtv-downloader/hltvdlm.py
```

(umask 0002 will ensure the files to be group writable)

### Source Code
Can be found on [GitHub](https://github.com/kettenbach-it/homeloadtv-downloader)


## License
GNU AGPL v3

Fore more, see [LICENSE](LICENSE)

