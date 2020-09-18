from flask import Blueprint, render_template, redirect, url_for, request
from flask_login import logout_user, current_user, login_required
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import requests, json
from .extensions import db
from .tasks import get_reservation, cancel_reservation
from .models import User, Reservation, RepeatingReservation

main = Blueprint('main', __name__)

@main.route('/')
@main.route('/index')
@login_required
def index():
    # print(current_user.reservations)
    return render_template('calendar-view.html')

@main.route("/addReservation", methods=['POST'])
@login_required
def add_reservation():
    start_time = datetime.strptime(request.form.get('datetime_str_start'), "%a, %d %b %Y %H:%M:%S GMT")
    end_time = datetime.strptime(request.form.get('datetime_str_end'), "%a, %d %b %Y %H:%M:%S GMT")

    repeating = False
    if request.form.get('repeating') == 'true':
        repeating = True

    new_reservation = Reservation(start_time=start_time, end_time=end_time, repeating_weekly=repeating, status=4) #queued status

    try:
        old_index = current_user.reservations.index(new_reservation)
        current_user.reservations[old_index].status = 0
    except ValueError:
        new_reservation.status = 0
        current_user.reservations.append(new_reservation)

    # if repeating, add to repeating as well
    if repeating:
        new_rec_reservation = RepeatingReservation(start_time=start_time, end_time=end_time)
        current_user.repeating_reservations.append(new_rec_reservation)

    db.session.commit()

    #TODO investigate weird time zone issues here
    if datetime.now() + timedelta(days=2) >= start_time:
        # need to get it now!
        get_reservation.delay(new_reservation.id, current_user.id)

    return json.dumps({'success':True}), 200, {'ContentType':'application/json'}

@main.route("/cancelReservation", methods=["POST"])
@login_required
def del_reservation():
    start_to_delete = datetime.strptime(request.form.get('datetime_str_start'), "%a, %d %b %Y %H:%M:%S GMT")

    for reservation in current_user.reservations:
        if reservation.start_time == start_to_delete:
            if reservation.status == 1:
                cancel_reservation.delay(reservation.id, reservation.user_id)
            else:
                reservation.status = 3
                db.session.commit()
    if request.form.get('repeating') == "true":
        for reservation in current_user.repeating_reservations:
            if reservation.start_time.time() == start_to_delete.time() and reservation.start_time.weekday() == start_to_delete.weekday():
                current_user.repeating_reservations.remove(reservation)
                break

    return json.dumps({'success':True}), 200, {'ContentType':'application/json'}

@main.route("/getScheduleData")
@login_required
def get_schedule_data():
    #   0 = queued
    #   1 = success
    #   2 = failed

    data_list = []

    # pull recurring events first
    def adjustToCurrWeek(dateTime):
        date = datetime.now()
        newDate = date + timedelta(days=(dateTime.weekday()-date.weekday()+7)%7)
        return newDate.replace(hour=dateTime.hour, minute=dateTime.minute, second=dateTime.second, tzinfo=dateTime.tzinfo)

    def adjustResToCurrWeek(reservation):
        reservation.start_time = adjustToCurrWeek(reservation.start_time)
        reservation.end_time = adjustToCurrWeek(reservation.end_time)
        return reservation

    # recurring_reservations = [adjustResToCurrWeek(res) for res in current_user.repeating_reservations]

    today_start = datetime.now().replace(hour=0, minute=0, second=0)
    end_week = today_start + timedelta(days=7)
    curr_week_reservations = [res for res in current_user.reservations if res.start_time >= today_start and res.start_time < end_week]

    # curr_week_reservations.extend(recurring_reservations)

    for reservation in curr_week_reservations:
        # format so fullcalendar likes the output
        # pull only data for range you need (ALSO REPEATING)
        event_exists = False
        for event in data_list:
            # if event already exists in expanded form
            if event['start'] == reservation.start_time.isoformat():
                # do not add recurring adjusted event if already expanded
                event_exists = True
                break
        if event_exists or reservation.status == 3:
            continue

        event = {
            # 'name': 'Repeating',
            'start': reservation.start_time.isoformat(),
            'end': reservation.end_time.isoformat(),
            'allDay': False,
            'isTemporary': False,
            #'color': "green",
            #'backgroundColor'
            #'borderColor'
        }

        if reservation.repeating_weekly:
            event['title'] = 'Repeating'

        if reservation.status == 1:
            event['color'] = 'green'
        if reservation.status == 2:
            event['color'] = 'red'

        data_list.append(event)
    return {'events': data_list}

@main.route("/getAvailabilityData/<day_num>.json")
@login_required
def get_data_for_day(day_num):
    # synchronous for now, but can be changed
    """
    asynch_res = scrape_appointment_data.delay(int(day_num))
    res = asynch_res.get()
    return res
    """
    url_list = [
        "https://recwell.purdue.edu/Program/GetProgramDetails?courseId=1e7d1515-87e5-405d-b35a-96cf18c1cd1a&semesterId=6830b6fc-7a4f-4340-ab62-92bf071dffed",
        "https://recwell.purdue.edu/Program/GetProgramDetails?courseId=52be22f5-728b-4ef7-8602-972011d8739e&semesterId=6830b6fc-7a4f-4340-ab62-92bf071dffed",
        "https://recwell.purdue.edu/Program/GetProgramDetails?courseId=646d15bd-6fa9-4558-aac8-e70d1a0847c5&semesterId=6830b6fc-7a4f-4340-ab62-92bf071dffed",
        "https://recwell.purdue.edu/Program/GetProgramDetails?courseId=b5c44d87-bead-49d7-b353-42eb5e595022&semesterId=6830b6fc-7a4f-4340-ab62-92bf071dffed",
        "https://recwell.purdue.edu/Program/GetProgramDetails?courseId=89d70d51-5760-495d-ba8e-d47fa1627cb4&semesterId=6830b6fc-7a4f-4340-ab62-92bf071dffed",
        "https://recwell.purdue.edu/Program/GetProgramDetails?courseId=65e7f3fa-4c6b-4fb6-b5bb-b5eea54ea46e&semesterId=6830b6fc-7a4f-4340-ab62-92bf071dffed",
        "https://recwell.purdue.edu/Program/GetProgramDetails?courseId=852d33d3-7615-4b2d-94e7-618d5e3feb1e&semesterId=6830b6fc-7a4f-4340-ab62-92bf071dffed"
    ]
    scrape_data = requests.get(url_list[int(day_num)])
    soup = BeautifulSoup(scrape_data.text, 'lxml')
    mydivs = soup.findAll("div", class_="program-schedule-card-caption")

    options_data = []
    for timecard in mydivs:
        date = timecard.h4.span.text.strip()
        time_range, _, spots_str = timecard.h4.small.text.strip().splitlines()
        start_time, end_time = [time.strip() for time in time_range.split("-")]
        spots = spots_str.split(" ")[0]
        if spots != 0:
            datetime_start = datetime.strptime(date + " " + start_time, "%A, %B %d, %Y %I:%M %p")
            datetime_end = datetime.strptime(date + " " + end_time, "%A, %B %d, %Y %I:%M %p")
            timeData = datetime_start.strftime("%H%M")
            options_data.append({"start": datetime_start.strftime("%a, %d %b %Y %H:%M:%S GMT"),
                                 "end": datetime_end.strftime("%a, %d %b %Y %H:%M:%S GMT"),
                                 "spots": spots,
                                 "displayStr": datetime_start.strftime("%-I:%M %p") + " - " + datetime_end.strftime("%-I:%M %p"),
                                 "timeData": timeData})

    return {"list": sorted(options_data, key = lambda i: (i['timeData']))}
