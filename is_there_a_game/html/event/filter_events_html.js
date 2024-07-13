// Replace Variables
//   SERVICE_URL
var service_url = 'SERVICE_URL'
var datetime_start = 'DATETIME_START'
var datetime_end = 'DATETIME_END'

async function filterEvents() {
    console.log('Filtering events');

    const form = document.getElementById('filter-events');
    const formData = new FormData(form);
    // const params = new URLSearchParams(formData);

    console.log(datetime_start)

    const paramsObject = {};

    if (datetime_start != 'undefined') {
        paramsObject['event_after'] = datetime_start;
    }
    if (datetime_end != 'undefined') {
        paramsObject['event_before'] = datetime_end;
    }

    // let yourDate = new Date()
    // paramsObject
    // Name
    if(formData.get('name') != null && formData.get('name') != ''
        && formData.get('name') != 'undefined') {
            paramsObject['name'] = formData.get('name');
    }
    // // Venue
    // paramsObject['venue'] = [];
    // if(document.getElementById('empower-field-checkbox').checked) {
    //     paramsObject['venue'].push('Empower Field at Mile High');
    // }
    // if(document.getElementById('ball-arena-checkbox').checked) {
    //     paramsObject['venue'].push('Ball Arena');
    // }

    // Routs


    const params = new URLSearchParams(paramsObject);
    console.log('params: ' + params.toString());


    url = service_url + "/event?" + params;
    console.log('url: ' + url);

    const response = await fetch(url, {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
        },
    });
    const data = await response.json();
    const status = response.status;
    console.log('Call status: ' + status);
    return data;
}

async function populateTable() {
    console.log('Populating table');

    // DIV
    console.log('Clearing table...');
    var table_div = document.getElementById('events-table-div');
    table_div.innerHTML = '';

    // TABLE
    var table_element = document.createElement('table');
    table_element.style.width = '100%';
    table_element.style.height = '100%';
    table_element.style.border = '5px solid black';

    // HEADER
    var events_table_header = document.createElement('thead');
    events_table_header.innerHTML = '<tr><th>Event Name</th><th>Location</th><th>Closure Start</th><th>Closure End</th><th>Event Start</th><th>Event End</th></tr>';
    events_table_header.style.width = '100%';
    events_table_header.style.fontWeight = 'bold';
    events_table_header.style.padding = '5px';
    table_element.appendChild(events_table_header);

    // BODY
    var events_table_body = document.createElement('tbody');
    const events_response = await filterEvents();
    const events_array = events_response.events;
    for(var i = 0; i < events_array.length; i++) {
        // ROW
        var events_table_row = document.createElement('tr');
        events_table_row.style.padding = '5px';
        events_table_row.style.border = '1px red double'

        console.log('ROW: ' + events_table_row);

        // Events Name
        var event_hyperlink = document.createElement("a");
        event_hyperlink.href = service_url + '/html/events/' + events_array[i].uid;
        event_hyperlink.innerHTML = events_array[i].name;

        var events_table_item = document.createElement('td');
        events_table_item.style.padding = '1px 25px';
        events_table_item.appendChild(event_hyperlink);
        events_table_row.appendChild(events_table_item);

        // Events Location
        var event_hyperlink = document.createElement("a");
        event_hyperlink.href = service_url + '/html/venue/' + events_array[i].uid;
        event_hyperlink.innerHTML = events_array[i].venue;

        var events_table_item = document.createElement('td');
        events_table_item.style.padding = '1px 25px';
        events_table_item.appendChild(event_hyperlink);
        events_table_row.appendChild(events_table_item);


        // Event Times
        var events_table_item = document.createElement('td');
        events_table_item.style.padding = '1px 25px';
        events_table_item.innerHTML = events_array[i].closures_start;
        events_table_row.appendChild(events_table_item);

        var events_table_item = document.createElement('td');
        events_table_item.style.padding = '1px 25px';
        events_table_item.innerHTML = events_array[i].closures_end;
        events_table_row.appendChild(events_table_item);

        var events_table_item = document.createElement('td');
        events_table_item.style.padding = '1px 25px';
        events_table_item.innerHTML = events_array[i].event_start;
        events_table_row.appendChild(events_table_item);

        var events_table_item = document.createElement('td');
        events_table_item.style.padding = '1px 25px';
        events_table_item.innerHTML = events_array[i].event_end;
        events_table_row.appendChild(events_table_item);

        // Additional Formatting
        if(i % 2 == 0) {
            events_table_row.style.backgroundColor = '#2c2d2e';
        }
        else {
            events_table_row.style.backgroundColor = '#35363b';
        }
        events_table_body.appendChild(events_table_row);
    }

    table_element.appendChild(events_table_body);
    table_div.appendChild(table_element);

    table_element.appendChild(events_table_body);
    table_div.appendChild(table_element);
}
window.onload = populateTable;

