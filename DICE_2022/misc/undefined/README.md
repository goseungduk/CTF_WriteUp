# undefined
## #nodejs #jail

---

node.js 를 활용한 jail 문제이다.

```javascript
#!/usr/local/bin/node
// index.js
// don't mind the ugly hack to read input
console.log("What do you want to run?");
let inpBuf = Buffer.alloc(2048);
const input = inpBuf.slice(0, require("fs").readSync(0, inpBuf)).toString("utf8");
inpBuf = undefined;

Function.prototype.constructor = undefined;
(async () => { }).constructor.prototype.constructor = undefined;
(function* () { }).constructor.prototype.constructor = undefined;
(async function* () { }).constructor.prototype.constructor = undefined;

for (const key of Object.getOwnPropertyNames(global)) {
    if (["global", "console", "eval"].includes(key)) {
        continue;
    }
    global[key] = undefined;
    delete global[key];
}

delete global.global;//global 삭제
process = undefined;//process 삭제

{
    let require = undefined;
    // ...
    // many built-in functions are undefineded
    // ...
    console.log(eval(input));
}
```

문제의 소스이다.

보면, 우선 `Function`, `AsyncFunction`, `Generator Function`, `AsyncGenerator` 객체 날리고 `global`, `process` 변수 날리고 마지막으로 node.js 실행과 동시에 생기는 **built-in 함수** 들까지 모두 날린다.

그렇게 되면 남는(사용가능한) 것은 아래와 같은 것들이다.

![](https://i.imgur.com/Ld2Ly2N.png)

사실상 쓸 수 있는게 `eval` 이랑 `console` 객체정도라고 보면 될듯하다.

