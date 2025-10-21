

s = "(("
stack =[]
for i in range(len(s)):
    if s[i] in "{([":
        stack.append(s[i])
    else:
        if stack[-1] == "{" and s[i] == "}":
            stack.pop(-1)
        elif stack[-1] == "(" and s[i] == ")":
            stack.pop(-1)
        elif stack[-1] == "[" and s[i] == "]":
            stack.pop(-1)
        else:
            print("wrong")
        
if stack:
    print("wrong")
else:
    print("right")