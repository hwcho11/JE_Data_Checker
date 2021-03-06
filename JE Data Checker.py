# coding: utf-8

from os import getcwd
from detect_delimiter import detect as detect_delimiter
from cchardet import detect as detect_encoding
from timeit import default_timer
from tkinter import filedialog, messagebox
from tkinter import Tk

_version = "20210218_06_D"


def load_file():
	window = Tk()
	window.withdraw()
	return filedialog.askopenfilename(initialdir=getcwd(), title="JE DATA CHECKER: 검사할 파일을 선택하세요",
	                                  filetype=(("JE data", ".txt .csv .tsv"), ("all files", "*")))


def write_file(name, line, cr=True):
	with open(name, "a+") as ff:
		ff.write(line + ("\n" if cr else ""))


def select_options():
	window = Tk()
	window.withdraw()
	return messagebox.askyesno(title="JE DATA CHECKER (D)", message="줄바꿈 오류가 있는 파일의 자동 cleansing을 시도합니까?\n줄바꿈 오류가 없다면 No를 클릭하세요")


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
print(" <D 버전 추가 기능>")
print(" 필요한 경우 줄바꿈 오류를 자동으로 치료 시도합니다 (구분자 오류 제외)")
print(" cleansing 완료된 결과를 cleansed 사본 파일에 출력합니다")
print(" 사본 파일은 자동으로 UTF-8 with Signature 인코딩 저장됩니다.")
print("=" * 80)

print("...")
print("검사할 파일을 선택하세요")
filename = load_file()
if filename == "":
	print("파일이 로드되지 않아 프로그램을 종료합니다")
	exit()
print(" 선택된 파일: " + filename)

doctor = select_options()
print("...")
if doctor :
	print("검사를 시작합니다 [줄바꿈 오류 cleansing 수행중]")
else :
	print("검사를 시작합니다")
start_time = default_timer()
encoding = ""
delimiter = ""
line_count = 0
error_count = 0
delimiter_count = 0
is_delimiter_in_last = False
error_line_numbers = []
outfile = filename + "_check log.txt"
cleansedfile = filename + "_cleansed.txt"
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

if doctor:
	try:
		print(" [4/4] 줄바꿈, 구분자 오류 확인중...", end="")
		write_file(outfile, "*발견된 오류 : Line 번호는 텍스트의 Line 위치입니다 (단축키 Ctrl+G)")
		write_file(outfile, "=" * 80)
		write_file(outfile, "No.\tLine 번호\t오류 유형\t\t\t첫번째 열 내용")
		write_file(outfile, "=" * 80)
		with open(filename, "rt", encoding=encoding, errors="ignore") as infile:
			with open(cleansedfile, "wt", encoding="UTF-8-SIG", errors="ignore") as cleansed:
				line_number = 1
				inline = infile.readline()
				cleansed.write(inline)
				reservedline = ""
				delimiter_count = inline.count(delimiter)
				is_delimiter_in_last = (inline[-2] == delimiter) if inline != "\n" else False
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
							(len(inline) > 1 and inline[-2] != delimiter and is_delimiter_in_last) or
							(curr_delimiter_count < delimiter_count)):
						error_line_numbers.append(line_number)
						if last_error_line != line_number - 1:
							error_count += 1
						write_file(outfile,
						           (str(error_count) if (last_error_line != line_number - 1) else "") +
						           "\t" + str(line_number) + ("\t" if line_number < 10000000 else "") +
						           "\t줄바꿈 문자가 필드에 존재\t" + inline.split(delimiter)[0].replace("\n", ""))
						last_error_line = line_number
						if reservedline == "":
							reservedline = inline.replace("\n", "")
						else:
							reservedline += inline.replace("\n", "")
							new_delimiter_count = reservedline.count(delimiter)
							if new_delimiter_count >= delimiter_count:
								cleansed.write(reservedline+"\n")
								reservedline = ""
					elif curr_delimiter_count > delimiter_count:
						error_line_numbers.append(line_number)
						error_count += 1
						write_file(outfile,
						           str(error_count) + "\t" + str(line_number) + ("\t" if line_number < 10000000 else "") +
						           "\t구분자가 필드에 존재\t\t" + inline.split(delimiter)[0].replace("\n", ""))
						last_delimiter_count = 0
						cleansed.write(inline)
					else:
						cleansed.write(inline)
		
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

else:
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
						(len(inline) > 1 and inline[-2] != delimiter and is_delimiter_in_last) or
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
if doctor:
	print(" 오류 치료 결과가 아래 cleansed 파일에 저장됩니다")
	print(cleansedfile)

print("...")
exitCode = input("창을 닫거나 엔터키를 입력해 프로그램을 종료하세요")
