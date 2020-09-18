document.addEventListener('DOMContentLoaded', function() {
  // offset for EST
  var offset = 240;
  var mainCalendarEl = document.getElementById('mainCalendar');
  var schedulerCalendarEl = document.getElementById('schedulerCalendar');
  var makeReservationCalendarEl = document.getElementById('makeReservationCalendar');
  let businessHours = [
    {
      daysOfWeek: [0], // Sunday
      startTime: '11:00', // 11am
      endTime: '22:00' // 10pm
    },
    {
      daysOfWeek: [1, 2, 3, 4, 5], // Monday, Tuesday, Wednesday, Thursday, Friday
      startTime: '06:00', // 6am
      endTime: '22:00' // 10pm
    },
    {
      daysOfWeek: [6], // Saturday
      startTime: '08:00', // 8am
      endTime: '20:00' // 8pm
    }
  ]

  // generate html for time button and return it
  function generateTimeButtonHtml(buttonDict) {
    let buttonHtml = '<div class="card btn btn-outline-primary';
    if (buttonDict.spots == 0) {
      buttonHtml += ' disabled';
    }
    buttonHtml += ' mb-1 time-button" data-toggle="button" aria-pressed="false" data-start="' +
          buttonDict.start + '" data-end="' + buttonDict.end + '"><div class="card-body pb-0 pt-0">' +
          buttonDict.displayStr + '<br><small>' +
          buttonDict.spots + ' spots</small></div></div>';
    // TODO add onclick events to select calendar
    return buttonHtml
  }

  // return true if in business hours else return false
  function inBusinessHours(date, businessHours) {
    let dateDay = date.getUTCDay();
    for (var i = 0; i < businessHours.length; i++) {
      // check if date should conform to this dict's start and end times
      if (businessHours[i].daysOfWeek.includes(dateDay)) {
        // toLocaleTimeString with arg it-IT will return 24hr time
        let dateStr = date.toUTCString()
        var arr = dateStr.split(" ")[4].split(":");
        arr.pop();
        timeStr = arr.join(":");

        // if time after or equal to business hour start for day
        if (businessHours[i].startTime <= timeStr) {
          // if time before or equal to business hour end for day
          if (businessHours[i].endTime >= timeStr) {
            return true
          }
        }
        //  if the day matches, but any of the times do not, dont check any more
        //    days and just return false immediately
        return false
      }
    }
    // if date clicked's weekday is not in businessHours at all
    return false;
  }

  // handler for a click on the main calendar
  function mainClickHandler(info) {
    // alert('Clicked on: ' + info.dateStr);
    let clickedDate = new Date(info.dateStr);

    if (!inBusinessHours(clickedDate, businessHours)) {
      return;
    }

    // Add offset, so the time we want is utc
    let currDate = new Date(new Date().getTime() - offset*60000);
    if (clickedDate < currDate) {
      console.log(clickedDate);
      console.log(currDate);
      return;
    }

    // get time difference between curr and clicked on
    let timeDiff = Math.abs(clickedDate.getTime() - currDate.getTime());
    if (timeDiff < (2 * 24 * 60 * 60 * 1000)) {
      // reservations already available for this time, show mini-view

      $("#btnTimeContainer").html('<div class="text-center"><div class="spinner-border" role="status"><span class="sr-only">Loading...</span></div></div>');

      let endpoint = "/getAvailabilityData/" + clickedDate.getUTCDay() + ".json";

      // get button data from endpoint
      $.getJSON( endpoint, function( data ) {
        var buttons = [];
        // key here is 24hr time w no colon "%H%M"
        $.each( data.list, function( index, val ) {
          buttons.push(generateTimeButtonHtml(val));
        });

        $("#btnTimeContainer").html(buttons.join(""));
      });

      makeReservationCalendar.gotoDate(clickedDate);
      $('#makeReservationCalendar').html('<div class="text-center"><div class="spinner-border" role="status"><span class="sr-only">Loading...</span></div></div>');
      $('#makeReservationModalTitle').text(clickedDate.toDateString());
      $('#makeReservationModal').modal('show');
    } else {
      // reservations not availble yet but we can schedule event
      return;


      if ((clickedDate.getUTCMinutes() == 0) && (clickedDate.getUTCSeconds() == 0)) {
        var len = 60;
      } else {
        var len = 80;
      }
      // just add calendar event to date and confirm
      var endDate = new Date(clickedDate.getTime() + len*60000);

      schedulerCalendar.addEvent({
        start: clickedDate,
        end: endDate,
        allDay: false,
        backgroundColor: '#99ccff',
        textColor: 'black',
        extendedProps: {
          isTemporary: true,
        },
      });

      schedulerCalendar.gotoDate(clickedDate);
      //schedulerCalendar.select(clickedDate, endDate);
      $('#schedulerCalendar').html('<div class="text-center"><div class="spinner-border" role="status"><span class="sr-only">Loading...</span></div></div>');
      $('#schedulerModalTitle').text(clickedDate.toDateString());
      $('#schedulerModal').modal('show');
    }
  }

  function eventClickHandler(info) {
    // TODO add modal form for recurring event deleting (and one for basic!)
    let clickedDate = new Date(info.event.start);

    let currDate = new Date(new Date().getTime() - offset*60000);
    if (clickedDate < currDate) {
      return;
    }

    // get time difference between curr and clicked on
    let timeDiff = Math.abs(clickedDate.getTime() - currDate.getTime());
    if (false) {//(timeDiff < (2 * 24 * 60 * 60 * 1000)) {
      // can't delete already confirmed events
      return;
    } else {
      var repeating;
      if (info.event.title == "Repeating") {
        repeating = true;
      } else {
        repeating = false;
      }
      if (confirm("Would you like to delete your reservation?\n" + info.event.start)) {
        $.ajax({
          type: "POST",
          url: "/cancelReservation",
          data: {
            datetime_str_start: info.event.start.toUTCString(),
            repeating: repeating,
          },
          dataType: "json",
        }).done(function() {
          // success
        })
        .fail(function() {
          alert( "Error deleting reservation" );
        })
        .always(function() {
          $.get({
            url:"/getScheduleData",
            dataType: 'json',
            success: function( data ) {
              $.each(mainCalendar.getEventSources(), function(index, eventSource) {
                eventSource.remove();
              });
              mainCalendar.addEventSource(data.events);
              mainCalendar.render();

              $.each(schedulerCalendar.getEventSources(), function(index, eventSource) {
                eventSource.remove();
              });
              $.each(makeReservationCalendar.getEventSources(), function(index, eventSource) {
                eventSource.remove();
              });
              schedulerCalendar.addEventSource(data.events);
              makeReservationCalendar.addEventSource(data.events);
            }
          });
          mainCalendar.render();
        });
      }
    }
  }

  function removeAllTemporaryEvents(calendar) {
    events = calendar.getEvents();
    $.each(events, function(index, event) {
      if (event.extendedProps.isTemporary) {
        event.remove();
      }
    });
  }

  function submitTemporaryEvents(calendar, repeating) {
    events = calendar.getEvents();
    $.each(events, function(index, event) {
      if (event.extendedProps.isTemporary) {
        // post form
        console.log(event.start.toUTCString());
        $.ajax({
          type: "POST",
          url: "/addReservation",
          data: {
            datetime_str_start: event.start.toUTCString(),
            datetime_str_end: event.end.toUTCString(),
            repeating: repeating,
          },
          dataType: "json",
        }).done(function() {
          // success
        })
        .fail(function() {
          alert( "Error submitting reservation" );
        })
        .always(function() {
          $.get({
            url:"/getScheduleData",
            dataType: 'json',
            success: function( data ) {
              $.each(mainCalendar.getEventSources(), function(index, eventSource) {
                eventSource.remove();
              });
              mainCalendar.addEventSource(data.events);
              mainCalendar.render();

              $.each(schedulerCalendar.getEventSources(), function(index, eventSource) {
                eventSource.remove();
              });
              $.each(makeReservationCalendar.getEventSources(), function(index, eventSource) {
                eventSource.remove();
              });
              schedulerCalendar.addEventSource(data.events);
              makeReservationCalendar.addEventSource(data.events);
            }
          });
          mainCalendar.render();
        });
      }
    });
  }

  // reset schedulerCalendar on modal show
  $('#schedulerModal').on("shown.bs.modal", function () {
    $('#schedulerCalendar').html('');
    schedulerCalendar.render();
    $('#schedulerModal').modal('handleUpdate');
  }).on("hide.bs.modal", function() {
    // remove all events
    removeAllTemporaryEvents(schedulerCalendar);
    schedulerCalendar.destroy();
  });

  $('#schedulerModalSubmit').on('click', function(event) {
    submitTemporaryEvents(schedulerCalendar, false);
    $('#schedulerModal').modal('hide');
  })
  $('#schedulerModalReserveWeekly').on('click', function(event) {
    submitTemporaryEvents(schedulerCalendar, true);
    $('#schedulerModal').modal('hide');
  })

  // reset makeReservationCalendar on modal show
  $('#makeReservationModal').on("shown.bs.modal", function () {
    $('#makeReservationCalendar').html('');
    makeReservationCalendar.render();
    $('#makeReservationModal').modal('handleUpdate');
  }).on("hide.bs.modal", function() {
    // remove all events
    removeAllTemporaryEvents(makeReservationCalendar);
    makeReservationCalendar.destroy();
  });

  $('#makeReservationModalSubmit').on('click', function(event) {
    submitTemporaryEvents(makeReservationCalendar, false);
    $('#makeReservationModal').modal('hide');
  });
  $('#makeReservationModalReserveWeekly').on('click', function(event) {
    submitTemporaryEvents(makeReservationCalendar, true);
    $('#makeReservationModal').modal('hide');
  })

  // add to makeReservationCalendar on time-button click
  $(document).on('click', "div.time-button", function() {
    if ($(this).hasClass('active')) {
      // add event
      makeReservationCalendar.addEvent({
        id: $(this).data('start'),
        start: new Date($(this).data('start')),
        end: new Date($(this).data('end')),
        allDay: false,
        backgroundColor: '#99ccff',
        textColor: 'black',
        extendedProps: {
          isTemporary: true,
        },
      });
    } else {
      // remove event
      makeReservationCalendar.getEventById($(this).data('start')).remove();
    }
  });

  var schedulerCalendar = new FullCalendar.Calendar(schedulerCalendarEl, {
    //timeZone: "America/New_York",
    timeZone: "America/New_York",
    themeSystem: 'bootstrap',
    height: 'auto',
    initialView: 'timeGridDay',
    allDaySlot: false,
    //nowIndicator: true,
    // scrollTime: '07:00:00',
    slotMinTime: '06:00:00',
    slotMaxTime: '22:00:00',
    unselectAuto: false,
    businessHours: businessHours,
    headerToolbar: {
      right: '',
      center: '',
      left: '',
    },
    dayMaxEvents: true // allow "more" link when too many events
  });
  var makeReservationCalendar = new FullCalendar.Calendar(makeReservationCalendarEl, {
    //timeZone: false, // America/New_York
    timeZone: "America/New_York",
    themeSystem: 'bootstrap',
    height: 'auto',
    initialView: 'timeGridDay',
    allDaySlot: false,
    //nowIndicator: true,
    // scrollTime: '07:00:00',
    slotMinTime: '06:00:00',
    slotMaxTime: '22:00:00',
    businessHours: businessHours,
    headerToolbar: {
      right: '',
      center: '',
      left: '',
    },
    dayMaxEvents: true // allow "more" link when too many events
  });
  var mainCalendar = new FullCalendar.Calendar(mainCalendarEl, {
    //timeZone: false, // America/New_York
    timeZone: "America/New_York",
    firstDay: new Date(new Date().getTime() - offset*60000).getDay(),
    themeSystem: 'bootstrap',
    height: 'auto',
    initialView: 'timeGrid',
    duration: { days: 3 },
    allDaySlot: false,
    // nowIndicator: true,
    slotDuration: '00:20:00',
    // scrollTime: '07:00:00',
    slotMinTime: '06:00:00',
    slotMaxTime: '22:00:00',
    businessHours: businessHours,
    headerToolbar: {
      right: '',
      center: 'title',
      left: '',
    },
    dayMaxEvents: true, // allow "more" link when too many events
    dateClick: mainClickHandler,
    eventClick: eventClickHandler
  });
  $.get({
    url:"/getScheduleData",
    dataType: 'json',
    success: function( data ) {
      schedulerCalendar.addEventSource(data.events);
      makeReservationCalendar.addEventSource(data.events);
      mainCalendar.addEventSource(data.events);

      mainCalendar.render();
    }
  });
  mainCalendar.render();
});
