# jsfun1

### #misc #javascript #python

---

[jsc](https://trac.webkit.org/wiki/JSC) 라는 프로그램을 이용하여 파이썬 상에서 자바스크립트를 실행시킬 수 있는 구조이다.

```python

jsCodeTemplate = """
const getDescriptors = Object.getOwnPropertyDescriptors;

{userCode}

;

;(()=> {{
    return function(obj) {{
    let flag = "{flag}";
    if (typeof obj != 'object')
        return false;

    for (key in getDescriptors(obj))
        return false;

    for (key in obj)
        return false;

    if (obj.get != 'function() {{ return a; }}')
        return false;

    if (obj.set != 'function(val) {{ a = 17171717; }}')
        return false;

    val = {randNumber};
    obj.set(val);

    if (obj.get() != val)
        return false;

    if ((!('flag' in obj)) && obj.flag == 27272727)
        print(flag); // get flag!!!!

    return false;
    }}
}})()(myObj);
"""

userJsCode = jsCodeTemplate.format(
        userCode=userCode, randNumber=random.getrandbits(64), flag=flag)
```

결론적으로 jsCodeTemplate 에서 `print(flag)` 가 정상적으로 실행될 수 있도록 **myObj** 를 userCode 부분에서 잘 정의해주어야한다.

myObj 를 검사하는 조건은 여러가지가 있는데 차근차근 보자.

```javascript
if (typeof obj != "object") return false;
```

myObj 변수가 `object` 타입인지 확인한다. 여기는 그리 어려운 부분은 아닌듯하다.

```javascript
for (key in getDescriptors(obj)) return false;

for (key in obj) return false;
```

이 부분이 까다롭다고 생각했다.

우회하는 방법은 두 가지인데, **프로토타입** 을 이용하는 방법과 이번 write up 끝까지 사용할 **Proxy** 를 쓰는 방법.
