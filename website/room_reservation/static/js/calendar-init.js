const csrfToken = document.getElementById('calendar').getAttribute('data-csrf');
const notifications = document.getElementById('notifications');
let mouseHovering = false;
let roomFilterSelection = -1;

notifications.addEventListener('mouseenter', () => mouseHovering = true);
notifications.addEventListener('mouseleave', () => mouseHovering = false);

function el(name, attrs, ...els) {
    const newEl = document.createElement(name);
    Object.keys(attrs).forEach(key => newEl.setAttribute(key, attrs[key]));
    els.forEach(el => newEl.appendChild(el));
    return newEl;
}

function text(content) {
    return document.createTextNode(content);
}

function addNotification(textContent, undoCallback) {
    const closeBtn = el('button', {
        type: 'button',
        class: 'btn btn-outline-light justify-content-end'
    }, el('i', {class: 'fas fa-times'}));
    const undoBtn = el('button', {
        type: 'button',
        class: 'btn btn-outline-light justify-content-end mr-2'
    }, el('i', {class: 'fas fa-undo-alt'}), text(' UNDO'));

    const notif = el('div', {class: 'notification-collapsed'},
        el('p', {}, text(textContent)),
        el('ul', {class: 'nav justify-content-end'},
            el('li', {class: 'nav-item'}, undoBtn),
            el('li', {class: 'nav-item'}, closeBtn)));
    notifications.prepend(notif);

    closeBtn.addEventListener('click', event => {
        notif.remove();
    });
    undoBtn.addEventListener('click', () => {
        undoCallback();
        notif.remove();
    });
    // This makes sure the css transition plays
    // 40ms seems arbitrary but when testing it seemed like this worked the best in Firefox
    // Any lower and the transition wouldn't reliably play.
    window.setTimeout(() => notif.className = "notification", 40);
    window.setTimeout(() => {
        if (!mouseHovering) {
            notif.remove();
        }
    }, 10000);
}

async function addEvent(event) {
    const body = JSON.stringify({
        room: event.extendedProps.room,
        start_time: event.start,
        end_time: event.end
    });
    const resp = await fetch(new Request('/reservations/create', {
        method: 'POST',
        credentials: 'include',
        headers: {'X-CSRFToken': csrfToken},
        body: body,
    }));
    if (resp.status !== 200) {
        alert("An unknown error occurred.");
        event.remove();
        return;
    }
    const text = await resp.text();
    return JSON.parse(text);
}

function filterEvents(json) {
    for (let i in json) {
        json[i].setProp('classNames', ((json[i].extendedProps.room === roomFilterSelection) || (roomFilterSelection === -1)) ? ['visible'] : ['hidden']);
    }
}

async function changeEvent(info) {
    const event = info.event;
    const pk = event.extendedProps.pk,
        start_time = event.start,
        end_time = event.end;

    const body = JSON.stringify({
        room: event.extendedProps.room,
        start_time: start_time,
        end_time: end_time,
    });
    const resp = await fetch(new Request(`/reservations/${pk}/update`, {
        method: 'POST',
        credentials: 'include',
        headers: {'X-CSRFToken': csrfToken},
        body: body,
    }));

    if (resp.status !== 200) {
        info.revert();
        alert("An unknown error occurred.");
        return;
    }
    const text = await resp.text();
    const message = JSON.parse(text);
    if (!message.ok) {
        info.revert();
        alert(message.message);
    }
}

document.addEventListener('DOMContentLoaded', function () {
    const calendarEl = document.getElementById('calendar');
    const Draggable = FullCalendarInteraction.Draggable;

    const containerEl = document.getElementById('external-events-list');
    if (containerEl !== null) {
        new Draggable(containerEl, {
            itemSelector: '.fc-event.draggable',
        });
    }
    const calendar = new FullCalendar.Calendar(calendarEl, {
        plugins: ['dayGrid', 'timeGrid', 'bootstrap', 'interaction'],
        themeSystem: 'bootstrap',
        header: {
            right: 'timeGridDay,dayGridWeek today,prev,next',
        },
        initialView: 'timeGridDay',
        defaultView: 'timeGridDay',
        weekNumbers: true,
        weekNumbersWithinDays: true,
        weekends: false,
        firstDay: 1,
        timeFormat: "HH:mm",
        slotLabelFormat: {
            hour: '2-digit',
            minute: '2-digit',
            hour12: false,
        },
        slotDuration: '00:15:00',
        eventTimeFormat: {
            hour: '2-digit',
            minute: '2-digit',
            hour12: false,
        },
        slotEventOverlap: false,
        eventLimit: true,
        minTime: '8:00',
        maxTime: '18:00',
        height: 800,
        timeZone: 'local',
        allDaySlot: false,
        nowIndicator: true,
        editable: false,
        droppable: true,
        displayEventEnd: true,
        display: 'auto',
        eventReceive: async function ({event}) {
            console.log(event)
            const message = await addEvent(event);
            if (!message.ok) {
                alert(message.message);
                event.remove();
                return;
            }
            event.setProp('title', event.title + ' (you)');
            event.setExtendedProp('pk', message.pk);
        },
        eventClick: async function ({event}) {
            if (!event.durationEditable) {
                return;
            }
            const pk = event.extendedProps.pk;
            const resp = await fetch(new Request(`/reservations/${pk}/delete`, {
                method: 'POST',
                credentials: 'include',
                headers: {'X-CSRFToken': csrfToken},
            }));
            if (resp.status !== 200) {
                alert("An unknown error occurred.");
                return;
            }
            const text = await resp.text();
            const message = JSON.parse(text);
            if (!message.ok) {
                alert(message.message);
                return;
            }
            event.remove();
            let name = "your";
            if (event.extendedProps.reservee) {
                name = event.extendedProps.reservee + "s";
            }
            const date = FullCalendar.formatDate(event.start, {month: 'short', day: 'numeric'});
            addNotification(`Deleted ${name} reservation from ${date}`, async () => {
                const message = await addEvent(event);
                if (!message.ok) {
                    alert(message.message);
                    event.remove();
                    return;
                }
                calendar.addEvent({
                    pk: message.pk,
                    title: event.title,
                    reservee: event.extendedProps.reservee,
                    room: event.extendedProps.room,
                    start: event.start,
                    end: event.end,
                    editable: true,
                });
            })
        },
        eventDrop: changeEvent,
        eventResize: changeEvent,
        events: JSON.parse(document.getElementById('calendar').getAttribute('data-events'))
    });

    const roomFilter = document.getElementById("room-filter");
    if (roomFilter !== null) {

        // Reset on page update
        roomFilter.value = -1;

        roomFilter.onchange = (_event) => {
            let res = parseInt(roomFilter.value);
            if (res !== roomFilterSelection) {
                roomFilterSelection = res;
                let events = calendar.getEvents();
                filterEvents(events);

                for (let i of containerEl.children) {
                    i.className = (
                        (JSON.parse(i.attributes.getNamedItem("data-event").value).extendedProps.room !== roomFilterSelection)
                        && roomFilterSelection !== -1) ?
                        i.className.replace("draggable", "")
                        :
                        (i.className.indexOf("draggable") !== -1 ? i.className : i.className += "draggable")
                }

            }
        }
    }

    calendar.render();
});