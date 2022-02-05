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
	mv 127.0.0.1:8050/_dash-layout 127.0.0.1:8050/_dash-layout.json
	mv 127.0.0.1:8050/_dash-dependencies 127.0.0.1:8050/_dash-dependencies.json
	cp _static/async* 127.0.0.1:8050/_dash-component-suites/dash/dcc/
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
