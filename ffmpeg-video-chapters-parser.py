from optparse import OptionParser, Values
import re
import subprocess
from typing import List, NamedTuple

SECONDS_IN_MINUTE = 60

class ChapterInfo(NamedTuple):
    internal_name: str
    start: float
    end: float
    name: str

    @property
    def duration_representation(self) -> str:
        start = int(self.start)

        hours = str(start // SECONDS_IN_MINUTE).rjust(2, '0')
        minutes = str(start % SECONDS_IN_MINUTE).rjust(2, '0')

        return f'{hours}:{minutes}'

def main():
    """
    Basic code was borrowed from
    https://gist.github.com/dcondrey/469e2850e7f88ac198e8c3ff111bda7c
    """
    options = _parse_command_line_options()
    chapters = find_chapters_in_file(options.infile)

    chapters_result = '  \n'.join(
        chapter.duration_representation + ' ' + chapter.name for chapter in chapters)

    print(chapters_result)

def _parse_command_line_options() -> Values:
    parser = OptionParser(
        usage="usage: ffmpeg-video-chapters-parser [options] filename", version='ffmpeg-video-chapters-parser 1.0')

    parser.add_option("-f", "--file", dest='infile', help="Input File", metavar="FILE")

    options, _ = parser.parse_args()

    if not options.infile:
        parser.error('[-] Filename required')

    return options

def find_chapters_in_file(filename: str) -> List[ChapterInfo]:
    output = _execute_ffmpeg(filename)

    matches = re.findall(
        r'.*Chapter #(\d+:\d+): start (\d+\.\d+), end (\d+\.\d+)\s*\n\s*Metadata:\n\s*title\s*:\s*(.*)\n', output)

    return _convert_ffmpeg_response(matches)

def _convert_ffmpeg_response(matches: List) -> List[ChapterInfo]:
    chapters: List[ChapterInfo] = []

    for internal_name, start, end, name in matches:
        chapter = ChapterInfo(internal_name=internal_name, start=float(start), end=float(end), name=name)
        chapters.append(chapter)

    return chapters

def _execute_ffmpeg(filename: str) -> str:
    try:
        command = ['ffmpeg', '-i', filename]
        return subprocess.check_output(
            command, stderr=subprocess.STDOUT, universal_newlines=True)
    except subprocess.CalledProcessError as e:
        return e.output

if __name__ == '__main__':
    main()