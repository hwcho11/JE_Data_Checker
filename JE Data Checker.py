# coding: utf-8

from os import getcwd
from detect_delimiter import detect as detect_delimiter
from cchardet import detect as detect_encoding
from timeit import default_timer
from tkinter import filedialog
from tkinter import Tk

_version = "20201230_19"


def load_file():
	window = Tk()
	window.withdraw()
	return filedialog.askopenfilename(initialdir=getcwd(), title="JE DATA CHECKER: 검사할 파일을 선택하세요",
	                                  filetype=(("JE data", ".txt .csv .tsv"), ("all files", "*")))


def write_file(name, line, cr=True):
	with open(name, "a+") as ff:
		ff.write(line + ("\n" if cr else ""))


print("[!] FOR INTERNAL USE ONLY (Technology Risk Team)")
print("=" * 80)
print(" JE DATA CHECKER ver." + _version)
print("=" * 80)
print("<프로그램 설명>")
print(" CSV 유형의 파일로 추출된 JE Data 에서 cleansing 필요한 오류가 있는지 검사합니다")
print(" 발견 가능한 오류 : 줄바꿈 또는 구분자(delimiter)와 같은 특수문자가 필드에 포함된 경우")
print(" 검사중 발견된 오류의 위치 및 오류의 내용을 log 파일에 출력합니다")
print(" 이 프로그램은 원본 파일의 내용 및 오류를 수정하지 않습니다")
print(" 이 프로그램을 이용한 검사에서 발견되지 않는 오류가 존재할 수 있습니다")
print("=" * 80)

# print("...")
# print("검사할 파일이 있는 경로를 입력하세요(프로그램 exe 파일과 같은 폴더에 있다면 엔터키만 입력)")
# filepath = ""
# _loop = True
# while _loop:
#    filepath = input(" 여기에 입력: ")
#    if filepath == "":
#       filepath = os.getcwd()
#    if os.path.isdir(filepath):
#       print(" 입력한 경로에서 " + str(len(os.listdir(filepath))) + "개의 파일 또는 폴더를 확인했습니다")
#       _loop = False
#    else:
#       print(" 존재하지 않는 경로입니다 e.g C:\\path\\to\\data")
#
# print("...")
# print("검사할 파일의 파일명을 입력하세요(확장자 포함)")
# filename = ""
# _loop = True
# while _loop:
#    filename = input(" 여기에 입력: ")
#    if (filepath == "" and filename not in os.listdir()) or filename not in os.listdir(filepath):
#       print(" 존재하지 않는 파일입니다 e.g 전표데이터.txt")
#    else:
#       _loop = False
# filepath = filepath.replace('\\', '/')
# filename = filepath + filename if filepath[-1] == '/' else filepath + "/" + filename
# print("DEBUG#filename# "+filename)

print("...")
print("검사할 파일을 선택하세요")
filename = load_file()
if filename == "":
	print("파일이 로드되지 않아 프로그램을 종료합니다")
	exit()
print(" 선택된 파일: " + filename)

print("...")
print("검사를 시작합니다")
start_time = default_timer()
encoding = ""
delimiter = ""
line_count = 0
error_count = 0
delimiter_count = 0
is_delimiter_in_last = False
error_line_numbers = []
# column_lengths = []
# description_column_number = -1
outfile = filename + "_check log.txt"
with open(outfile, "wt") as f:
	f.write("[주의] 프로그램을 통한 검사에서 발견되지 않는 오류가 존재할 수 있습니다\n")
	
write_file(outfile, "*프로그램 버전: " + _version)
write_file(outfile, "*검사한 파일: " + filename)

try:
	print(" [1/4] 인코딩 확인중... ", end="")
	with open(filename, "rb") as infile:
		confidence = 0.0
		while confidence < 0.99:
			result = detect_encoding(infile.read(100000))
			confidence = float(result["confidence"] if result["confidence"] is not None else 0.0)
		encoding = result["encoding"]
		
	encoding = "cp949" if "UTF-8" not in encoding else encoding
	encoding_as = ""
	if encoding == "UTF-8-SIG":
		encoding_as = "UTF-8 with Signature"
	elif encoding == "UTF-8":
		encoding_as = "UTF-8 without Signature ([주의] UTF-8 with Signature 인코딩이 아닙니다)"
	else:
		encoding_as = "CP949 ([주의] UTF-8 with Signature 인코딩이 아닙니다)"
	print("\r [1/4] 인코딩 확인: " + encoding_as)
	write_file(outfile, "*인코딩 확인: " + encoding_as)
except Exception as e:
	write_file(outfile, "*인코딩 확인 중 아래와 같은 프로그램 오류가 발생했습니다:\n" + str(e))
	print("\r 프로그램 오류로 인해 인코딩 확인에 실패했습니다")

try:
	print(" [2/4] 구분자(Delimiter) 확인중...", end="")
	with open(filename, "rt", encoding=encoding, errors="ignore") as infile:
		delimiter = detect_delimiter(infile.readline(), whitelist=['|', '\t', ';', ','])
		
	delimiter_as = ""
	if delimiter == "|":
		delimiter_as = "PIPE(|)"
	elif delimiter == "\t":
		delimiter_as = "TAB"
	elif delimiter == ";":
		delimiter_as = "SEMICOLON(;)"
	elif delimiter == ",":
		delimiter_as = "COMMA(,)"
	else:
		delimiter_as = delimiter
	print("\r [2/4] 구분자 확인: " + delimiter_as + " " * 20)
	write_file(outfile, "*구분자 확인: " + delimiter_as)
except Exception as e:
	write_file(outfile, "*구분자 확인 중 아래와 같은 프로그램 오류가 발생했습니다:\n" + str(e))
	print("\r 프로그램 오류로 인해 구분자 확인에 실패했습니다")

try:
	print(" [3/4] Line 수 확인중", end="")
	with open(filename, "rt", encoding=encoding, errors="ignore") as infile:
		# line_count = sum(1 for _line in infile)
		line_count = 0
		curr_progress = -1
		inline = infile.readline()
		while inline:
			line_count += 1
			inline = infile.readline()
			progress = line_count // 100000
			if curr_progress != progress:
				curr_progress = progress
				print("\r [3/4] Line 수 확인중" + ("." * (progress % 5)) + "     ", end="")
	
	print("\r [3/4] Line 수 확인: " + str(line_count) + " ([주의] 텍스트 Line 수로, JE Line 수와 다를 수 있습니다)")
	write_file(outfile, "*Line 수 확인: " + str(line_count) + " ([주의] 텍스트 Line 수로, JE Line 수와 다를 수 있습니다)")
except Exception as e:
	write_file(outfile, "*Line 수 확인 중 아래와 같은 프로그램 오류가 발생했습니다:\n" + str(e))
	print("\r 프로그램 오류로 인해 Line 수 확인에 실패했습니다")

try:
	print(" [4/4] 줄바꿈, 구분자 오류 확인중...", end="")
	write_file(outfile, "*발견된 오류 : Line 번호는 텍스트의 Line 위치입니다 (단축키 Ctrl+G)")
	write_file(outfile, "=" * 80)
	write_file(outfile, "No.\tLine 번호\t오류 유형\t\t\t첫번째 열 내용")
	write_file(outfile, "=" * 80)
	with open(filename, "rt", encoding=encoding, errors="ignore") as infile:
		line_number = 1
		inline = infile.readline()
		delimiter_count = inline.count(delimiter)
		is_delimiter_in_last = (inline[-2] == delimiter) if inline != "\n" else False
		# column_lengths = [0] * delimiter_count if is_delimiter_in_last else [0] * (delimiter_count + 1)
		last_error_line = 0
		curr_progress = -1
		while line_number < line_count:
			line_number += 1
			inline = infile.readline()
			curr_delimiter_count = inline.count(delimiter)
			progress = int(line_number * 100 / line_count)
			if progress != curr_progress:
				print("\r [4/4] 줄바꿈, 구분자 오류 확인중..." + str(progress) + "%" +
				      ((" 현재까지 발견된 오류 수: " + str(error_count)) if error_count > 0 else ""), end="")
				curr_progress = progress
			if line_number < line_count and (
					(inline == "\n") or
					(len(inline) > 2 and inline[-2] != delimiter and is_delimiter_in_last) or
					(curr_delimiter_count < delimiter_count)):
				error_line_numbers.append(line_number)
				if last_error_line != line_number - 1:
					error_count += 1
				write_file(outfile,
				           (str(error_count) if (last_error_line != line_number - 1) else "") +
				           "\t" + str(line_number) + ("\t" if line_number < 10000000 else "") +
				           "\t줄바꿈 문자가 필드에 존재\t" + inline.split(delimiter)[0].replace("\n", ""))
				last_error_line = line_number
			elif curr_delimiter_count > delimiter_count:
				error_line_numbers.append(line_number)
				error_count += 1
				write_file(outfile,
				           str(error_count) + "\t" + str(line_number) + ("\t" if line_number < 10000000 else "") +
				           "\t구분자가 필드에 존재\t\t" + inline.split(delimiter)[0].replace("\n", ""))
				last_delimiter_count = 0
		# 	elif curr_delimiter_count == delimiter_count:
		# 	   line_list = inline.split(delimiter)
		# 	   for i in range(len(column_lengths)):
		# 	      column_lengths[i] = max(column_lengths[i], len(line_list[i]))
		# max_length = 0
		# for i in range(len(column_lengths)):
		#    if column_lengths[i] > max_length:
		#       max_length = column_lengths[i]
		#       description_column_number = i+1
	
	write_file(outfile, "End of Line")
	write_file(outfile, "=" * 80)
	if error_count > 0:
		print("\r [4/4] 발견된 오류 수: " + str(error_count) + " (자세한 오류 위치는 log 파일을 확인하세요)")
	else:
		print("\r [4/4] 발견된 오류 수: 0" + " " * 60)
	write_file(outfile, "*발견된 오류 수: " + str(error_count))
except Exception as e:
	write_file(outfile, "검사 중 아래와 같은 프로그램 오류가 발생했습니다:\n" + str(e))
	print("\r 프로그램 오류로 인해 검사가 중단되었습니다")

print("...")
print("검사가 완료되었습니다")
end_time = default_timer()
print(" 검사 소요시간(초): " + str(end_time - start_time))
write_file(outfile, "*검사 소요시간(초): " + str(end_time - start_time))
write_file(outfile, "검사가 완료되었습니다")
print(" 검사 결과가 아래 check log 파일에 저장됩니다")
print(outfile)

print("...")
# if error_count == 0:
#    exitCode = input("엔터키를 입력해 프로그램을 종료하세요")
# else:
#    print("발견된 오류에 대해 자동 수정을 시도합니다")
exitCode = input("창을 닫거나 엔터키를 입력해 프로그램을 종료하세요")
