fStr = "|-(a+0')*(a+0')=(a*a)+(0''*a)+0'"

sStr = []

sStr.append("@a((a+0')*(a+0')=(a*a)+(0''*a)+0')->")
sStr.append("((a+0')*(a+0')=(a*a)+(0''*a)+0')")
sStr.append("((a+0')*(a+0')=(a*a)+(0''*a)+0')")

f = open('number.txt', 'r')
count = int(f.read())
f.close()

formatN = '0'
for i in range(count):
    formatN += "'"

proof = fStr.replace('a', formatN)
f = open('input.txt', 'r')
add = f.read()
f.close()
proof += add
proof += sStr[0]
proof += sStr[1].replace('a', formatN)
proof += '\n'
proof += sStr[2].replace('a', formatN)
proof += '\n'


f = open('output.txt', 'w')
f.write(proof)
f.close()

