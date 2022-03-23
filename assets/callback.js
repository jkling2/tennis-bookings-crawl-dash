if (!window.dash_clientside) {
    window.dash_clientside = {}
}

window.dash_clientside.clientside = {
    update_store_data_initial: function(n_intervals) {
        var today = new Date();
        var reference_day = today.toLocaleString('de-DE', {weekday:'long'});
        var minutes = parseInt(today.getMinutes() / 15) * 15;
        var reference_day_time = ((today.getHours() < 10 ? "0" : "") + today.getHours()) + ":" + ((minutes < 10 ? "0" : "") + minutes);
        return [reference_day, reference_day_time];
    },
    update_store_data: function(reference_day, reference_day_time, store_data, days_d_to_en_dic) {
        if (!reference_day || !reference_day_time) {
        return [{}, ""];
        }
        var start_times = [];
        var dt = new Date();
        dt.setHours(reference_day_time.split(':')[0]);
        dt.setMinutes(reference_day_time.split(':')[1] - 30);
        for (let s = 0; s <= 6; s++) {
            start_times.push((dt.getHours() < 10 ? '0' + dt.getHours() : dt.getHours()) + ":" + (dt.getMinutes() < 10 ? '0' + dt.getMinutes() : dt.getMinutes()));
            dt.setMinutes(dt.getMinutes() + 15);
        }
        let day_data = store_data[days_d_to_en_dic[reference_day]];
        let data_for_day_time = {};
        data_for_day_time['layout'] = day_data['layout'];
        let data = [];
        for (let m = 0; m < day_data['data'].length; m++) {
            let mode = day_data['data'][m];
            let mode_for_day_time = {};
            mode_for_day_time['marker'] = mode['marker']
            mode_for_day_time['name'] = mode['name']
            mode_for_day_time['type'] = mode['type']
            let data_y = [].fill(0.0);
            for (let i = 0; i < mode['x'].length; i++) {
                let idx = start_times.indexOf(mode['x'][i]);
                if (idx >= 0) {
                    data_y[idx] = mode['y'][i];
                }
            }
            mode_for_day_time['x'] = [];
            for (let s = 0; s < start_times.length; s++) {
                if (s == 2) {
                    mode_for_day_time['x'].push("<b>" + start_times[s] + "</b>");
                } else {
                    mode_for_day_time['x'].push(start_times[s]);
                }
            }
            mode_for_day_time['y'] = data_y;
            data.push(mode_for_day_time);
        }
        data_for_day_time['data'] = data;
        return [data_for_day_time, `Ø Reservierungen für ${reference_day} gegen ${reference_day_time} Uhr`];
    }
};