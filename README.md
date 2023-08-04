# Gateway

## Freeze

* code-freeze gets frozen in
* code overrides frozen code
* Not sure how to freeze nested package (`tasks`) and relative imports, for that reason `app` is not frozen at the moment
* startup much faster with frozen code (despite `app`), perhaps `adafruit` and `lib` are the culprits.

## WiFi

* 8/3/2023: **SF router/ap is flaky**: no connections from any ESP32 until power cycling
* Xiao - both, but the `s3_prod` less so - have difficulty connecting to wifi, even more on GL.iNet router
* ProS3 wifi works well with both routers
* mdns (`rv-logger`) works with the GL.iNet

## TODO

* PWA
  * https://www.manning.com/books/progressive-web-apps (free online)

