# -*- coding: utf-8 -*-

# Reduced version of clamd
# https://github.com/graingert/python-clamd/blob/master/src/clamd/__init__.py
import re
import sys
import socket
import struct
import contextlib


scan_response = re.compile(r"^(?P<path>.*): ((?P<virus>.+) )?(?P<status>(FOUND|OK|ERROR))$")


class ClamdError(Exception):
    pass


class ConnectionError(ClamdError):
    """ Error from communication with clamd """


class ClamdScanner:
    def __init__(self, path='/var/run/clamd.scan/clamd.sock',
                 timeout=None):
        self.unix_socket = path
        self.timeout = timeout


    def _init_socket(self):
        try:
            self.clamd_socket = socket.socket(socket.AF_UNIX,
                                              socket.SOCK_STREAM)
            self.clamd_socket.connect(self.unix_socket)
            self.clamd_socket.settimeout(self.timeout)
        except socket.error:
            e = sys.exc_info()[1]
            raise ConnectionError(self._error_message(e))


    def _error_message(self, exception):
        if len(exception.args) == 1:
            return "Error connecting to {path}. {msg}".format(
                path=self.unix_socket,
                msg=exception.args[0]
            )
        else:
            return "Error {errno} connecting {path}. {msg}".format(
                errno=exception.args[0],
                path=self.unix_socket,
                msg=exception.args[1]
            )


    def ping(self):
        return self._basic_command("PING")


    def version(self):
        return self._basic_command("VERSION")


    def _basic_command(self, command):
        self._init_socket()
        try:
            self._send_command(command)
            response = self._recv_response().rsplit("ERROR", 1)
            if len(response) > 1:
                raise ResponseError(response[0])
            else:
                return response[0]
        finally:
            self._close_socket()


    def is_clean(self, buff):
        result = self.instream(buff)
        check_status = result['stream'][0]
        error = result['stream'][1]
        if check_status == 'FOUND':
            return False, error
        return True, None


    def instream(self, buff):
        try:
            self._init_socket()
            self._send_command('INSTREAM')

            # convert to byte stream
            import StringIO
            if isinstance(buff, unicode):
                buff = StringIO.StringIO(buff)
            print(type(buff))

            max_chunk_size = 1024  # < then StreamMaxLength in scan.conf

            chunk = buff.read(max_chunk_size).encode("utf8")
            while chunk:
                size = struct.pack(b'!L', len(chunk))
                self.clamd_socket.send(size + chunk)
                chunk = buff.read(max_chunk_size)

            self.clamd_socket.send(struct.pack(b'!L', 0))

            result = self._recv_response()

            if len(result) > 0:
                if result == 'INSTREAM size limit exceeded. Error':
                    raise BufferTooLongError(result)

                filename, reason, status = self._parse_response(result)
                return {filename: (status, reason)}
        finally:
            self._close_socket()


    def _send_command(self, cmd, *args):
        concat_args = ''
        if args:
            concat_args = ' ' + ' '.join(args)

        cmd = 'n{cmd}{args}\n'.format(cmd=cmd, args=concat_args).encode('utf-8')
        self.clamd_socket.send(cmd)


    def _recv_response(self):
        try:
            with contextlib.closing(self.clamd_socket.makefile('rb')) as f:
                return f.readline().decode('utf-8').strip()
        except (socket.error, socket.timeout):
            e = sys.exc_info()[1]
            raise ConnectionError("Error while reading from socket: {}".format(e.args))


    def _close_socket(self):
        self.clamd_socket.close()
        return


    def _parse_response(self, msg):
        try:
            return scan_response.match(msg).group("path", "virus", "status")
        except AttributeError:
            raise ResponseError(msg.rsplit("Error", 1)[0])


def file_scan(file):
    cd = ClamdScanner()
    try:
        result = cd.is_clean(file.file)
        return result
    except Exception as e:
        print('Error: {}'.format(e))
        return e


def test():
    return 'Test'
