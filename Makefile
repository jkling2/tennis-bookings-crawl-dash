html:
	# Build the app
	export DEBUG=False && python3 dash_app_clientside_callback.py &
	sleep 15
	wget -r http://127.0.0.1:8050/
	wget -r http://127.0.0.1:8050/_dash-layout
	wget -r http://127.0.0.1:8050/_dash-dependencies
	sed -i 's/_dash-layout/_dash-layout.json/g' 127.0.0.1:8050/_dash-component-suites/dash/deps/*.js
	sed -i 's/_dash-layout/_dash-layout.json/g' 127.0.0.1:8050/_dash-component-suites/dash/dash-renderer/build/*.js
	sed -i 's/_dash-dependencies/_dash-dependencies.json/g' 127.0.0.1:8050/_dash-component-suites/dash/deps/*.js
	sed -i 's/_dash-dependencies/_dash-dependencies.json/g' 127.0.0.1:8050/_dash-component-suites/dash/dash-renderer/build/*.js
	sed -i 's/_dash-component-suites/tennis-bookings-crawl-dash-page\/_dash-component-suites/g' 127.0.0.1:8050/index.html
	sed -i 's/"requests_pathname_prefix":"\/","ui":true,"props_check":true,"show_undo_redo":false,"suppress_callback_exceptions":false,"update_title":"Updating...","hot_reload":{"interval":3000,"max_retry":8}/"requests_pathname_prefix":"\/tennis-bookings-crawl-dash-page\/","ui":false,"props_check":false,"show_undo_redo":false/g' 127.0.0.1:8050/index.html
	sed -i 's/\?m=[0-9]*\.[0-9]*//g' 127.0.0.1:8050/index.html
	mv 127.0.0.1:8050/_dash-layout 127.0.0.1:8050/_dash-layout.json
	mv 127.0.0.1:8050/_dash-dependencies 127.0.0.1:8050/_dash-dependencies.json
	cp _static/async* 127.0.0.1:8050/_dash-component-suites/dash/dcc/
	cp assets/* 127.0.0.1:8050/
	ps | grep python | awk '{print $$1}' | xargs kill -9

update:
	git pull

clean:
	rm -rf 127.0.0.1:8050/

gh-pages:
	cd 127.0.0.1:8050 && git init && git add * && git commit -m "update" && git remote add origin https://github.com/jkling2/tennis-bookings-crawl-dash.github.io.git && git push -f origin master

all: gh-pages

teardown-python:
	ps | grep python | awk '{print $$1}' | xargs kill -9
