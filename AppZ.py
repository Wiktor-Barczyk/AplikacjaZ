import streamlit as st
from streamlit_calendar import calendar as st_calendar
from datetime import datetime, date, timedelta
import html

st.set_page_config(page_title="App", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
.stApp header, .stApp footer, .stApp [data-testid="stHeader"] {
    visibility: hidden;
    height: 0px;
}
.stApp {
    background-color: #0d1117;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
}
.stApp div.block-container {
    max-width: 720px;
    padding: 2.5rem 2rem;
    background-color: #161b22;
    border: 1px solid #30363d;
    border-radius: 16px;
    margin-top: 5vh;
    margin-bottom: 5vh;
    box-shadow: 0 16px 40px rgba(0,0,0,0.5);
}
.app-title {
    font-size: 1.8rem;
    font-weight: 700;
    color: #f0f6fc;
    margin-bottom: 2rem;
    text-align: center;
}
.section-header {
    font-size: 0.85rem;
    font-weight: 600;
    color: #58a6ff;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-top: 2.5rem;
    margin-bottom: 1rem;
    border-bottom: 1px solid #21262d;
    padding-bottom: 0.5rem;
}
.event-card {
    background-color: #0d1117;
    padding: 1rem;
    border-radius: 8px;
    border: 1px solid #30363d;
    margin-bottom: 0.75rem;
}
.event-title {
    font-size: 0.95rem;
    font-weight: 600;
    color: #f0f6fc;
}
.event-date {
    font-size: 0.8rem;
    color: #8b949e;
    margin-top: 0.25rem;
}
.empty-state {
    color: #8b949e;
    text-align: center;
    padding: 1.5rem;
    font-size: 0.9rem;
    background-color: #0d1117;
    border-radius: 8px;
    border: 1px dashed #30363d;
}
.stTextInput input,
.stDateInput input {
    background-color: #0d1117 !important;
    color: #f0f6fc !important;
    border: 1px solid #30363d !important;
    border-radius: 8px !important;
    height: 44px !important;
}
label {
    color: #8b949e !important;
    font-size: 0.85rem !important;
}
button[kind="primaryFormSubmit"] {
    background-color: #238636 !important;
    color: white !important;
    border: 1px solid rgba(240,246,252,0.1) !important;
    border-radius: 8px !important;
    height: 44px !important;
    font-weight: 600 !important;
    width: 100% !important;
    margin-top: 1rem !important;
}
button[kind="primaryFormSubmit"]:hover {
    background-color: #2ea043 !important;
}
.stButton > button {
    background-color: #21262d;
    color: #c9d1d9;
    border: 1px solid #30363d;
    border-radius: 8px;
}
.stButton > button:hover {
    background-color: #30363d;
    color: #f0f6fc;
}
@media (max-width: 650px) {
    .stApp div.block-container {
        max-width: 100%;
        width: calc(100vw - 16px);
        padding: 1rem 0.75rem;
        margin: 8px auto;
        border-radius: 12px;
    }
    .app-title {
        font-size: 1.35rem;
        margin-bottom: 1.2rem;
    }
    .section-header {
        font-size: 0.75rem;
        margin-top: 1.5rem;
    }
}
</style>
""", unsafe_allow_html=True)


def check_password():
    def password_guessed():
        if (
            st.session_state["username"] in st.secrets["passwords"]
            and st.session_state["password"] == st.secrets["passwords"][st.session_state["username"]]
        ):
            st.session_state["password_correct"] = True
            st.session_state["logged_user"] = st.session_state["username"]
            del st.session_state["password"]
            del st.session_state["username"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state or not st.session_state["password_correct"]:
        st.markdown('<div class="app-title">Logowanie</div>', unsafe_allow_html=True)
        st.text_input("Użytkownik", key="username")
        st.text_input("Hasło", type="password", key="password", on_change=password_guessed)

        if "password_correct" in st.session_state and not st.session_state["password_correct"]:
            st.error("Niepoprawne dane logowania.")
        return False

    return True


if not check_password():
    st.stop()


if "selected_date" not in st.session_state:
    st.session_state["selected_date"] = date.today().strftime("%Y-%m-%d")


@st.cache_resource
def get_db():
    return []


db = get_db()


def fix_calendar_date(*values):
    """
    Naprawia przesunięcie UTC:
    klik 2026-07-08 potrafi wrócić jako 2026-07-07T22:00:00.000Z.
    """
    fallback = ""

    for value in values:
        if not value:
            continue

        value = str(value)

        if "T" not in value:
            fallback = value[:10]
            continue

        try:
            dt = datetime.fromisoformat(value.replace("Z", "+00:00"))

            if value.endswith("Z") and dt.hour >= 20:
                dt = dt + timedelta(days=1)

            return dt.strftime("%Y-%m-%d")
        except ValueError:
            fallback = value[:10]

    return fallback


user_display_name = st.session_state["logged_user"].capitalize()

st.markdown(
    f'<div class="app-title">Witaj, {html.escape(user_display_name)}</div>',
    unsafe_allow_html=True,
)


st.markdown('<div class="section-header">Zbliżające się wydarzenia</div>', unsafe_allow_html=True)

today_str = date.today().strftime("%Y-%m-%d")
active_events = [e for e in db if e["Termin"] >= today_str]
upcoming_events = sorted(active_events, key=lambda x: x["Termin"])[:3]

if upcoming_events:
    for event in upcoming_events:
        st.markdown(
            f"""
            <div class="event-card">
                <div class="event-title">{html.escape(event["Wydarzenie"])}</div>
                <div class="event-date">{html.escape(event["Termin"])}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
else:
    st.markdown(
        '<div class="empty-state">Brak nadchodzących wydarzeń.</div>',
        unsafe_allow_html=True,
    )


st.markdown('<div class="section-header">Dodaj do kalendarza</div>', unsafe_allow_html=True)

with st.form("add_event_form", clear_on_submit=True):
    event_text = st.text_input("Nazwa wydarzenia", placeholder="Co planujecie?")
    event_date = st.date_input("Data wydarzenia", date.today())
    submit = st.form_submit_button("Dodaj wydarzenie")

    if submit and event_text.strip():
        new_id = max([e["id"] for e in db]) + 1 if db else 1

        db.append({
            "id": new_id,
            "Wydarzenie": event_text.strip(),
            "Termin": event_date.strftime("%Y-%m-%d"),
        })

        st.session_state["selected_date"] = event_date.strftime("%Y-%m-%d")
        st.rerun()


st.markdown('<div class="section-header">Przeglądaj kalendarz</div>', unsafe_allow_html=True)


calendar_events = []

for e in db:
    event_start = e["Termin"]
    event_end = (
        datetime.strptime(e["Termin"], "%Y-%m-%d").date() + timedelta(days=1)
    ).strftime("%Y-%m-%d")

    calendar_events.append({
        "id": str(e["id"]),
        "title": e["Wydarzenie"],
        "start": event_start,
        "end": event_end,
        "allDay": True,
        "backgroundColor": "#1a73e8",
        "borderColor": "#1a73e8",
        "textColor": "#ffffff",
    })


calendar_options = {
    "initialView": "dayGridMonth",
    "initialDate": st.session_state["selected_date"],
    "timeZone": "UTC",
    "locale": "pl",
    "firstDay": 1,
    "height": 520,
    "selectable": True,
    "editable": False,
    "dayMaxEvents": 2,
    "weekends": True,
    "headerToolbar": {
        "left": "prev,next today",
        "center": "title",
        "right": "",
    },
    "buttonText": {
        "today": "Dzisiaj",
        "month": "Miesiąc",
        "week": "Tydzień",
        "day": "Dzień",
        "list": "Lista",
    },
    "eventDisplay": "block",
    "displayEventTime": False,
    "fixedWeekCount": False,
}


custom_css = """
.fc {
    background: #0d1117;
    color: #c9d1d9;
    border: 1px solid #30363d;
    border-radius: 16px;
    overflow: hidden;
    padding: 12px;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Arial, sans-serif;
}
.fc .fc-toolbar {
    margin-bottom: 12px;
}
.fc .fc-toolbar-title {
    color: #f0f6fc;
    font-size: 1.15rem;
    font-weight: 700;
}
.fc .fc-button {
    background: transparent;
    color: #c9d1d9;
    border: none;
    border-radius: 999px;
    box-shadow: none;
    padding: 6px 10px;
}
.fc .fc-button:hover {
    background: #21262d;
    color: #f0f6fc;
}
.fc .fc-button-primary:not(:disabled).fc-button-active,
.fc .fc-button-primary:not(:disabled):active {
    background: #21262d;
    color: #f0f6fc;
}
.fc .fc-today-button {
    border: 1px solid #30363d;
    border-radius: 8px;
}
.fc-theme-standard td,
.fc-theme-standard th,
.fc-scrollgrid {
    border-color: #21262d !important;
}
.fc-col-header-cell {
    background: #0d1117;
}
.fc-col-header-cell-cushion {
    color: #8b949e;
    font-size: 0.78rem;
    font-weight: 600;
    padding: 10px 0;
    text-decoration: none;
}
.fc-daygrid-day {
    background: #0d1117;
}
.fc-daygrid-day:hover {
    background: #161b22;
    cursor: pointer;
}
.fc-daygrid-day-number {
    color: #c9d1d9;
    text-decoration: none;
    font-size: 0.86rem;
    width: 30px;
    height: 30px;
    border-radius: 999px;
    display: flex;
    align-items: center;
    justify-content: center;
    margin: 5px;
}
.fc-day-today {
    background: #0d1117 !important;
}
.fc-day-today .fc-daygrid-day-number {
    background: #1a73e8;
    color: white;
    font-weight: 700;
}
.fc-event {
    border-radius: 999px;
    padding: 2px 6px;
    font-size: 0.70rem;
    line-height: 1.2;
    border: none !important;
}
.fc-event-title {
    font-weight: 500;
}
.fc-daygrid-more-link {
    color: #8b949e;
    font-size: 0.68rem;
}
@media (max-width: 650px) {
    .fc {
        padding: 8px;
        border-radius: 12px;
    }
    .fc .fc-toolbar-title {
        font-size: 0.95rem;
    }
    .fc .fc-button {
        padding: 4px 7px;
        font-size: 0.75rem;
    }
    .fc-col-header-cell-cushion {
        font-size: 0.68rem;
        padding: 8px 0;
    }
    .fc-daygrid-day-number {
        width: 25px;
        height: 25px;
        font-size: 0.75rem;
        margin: 3px;
    }
    .fc-event {
        font-size: 0;
        width: 5px;
        height: 5px;
        padding: 0;
        border-radius: 50%;
        margin-left: 10px;
    }
    .fc-daygrid-day-frame {
        min-height: 54px !important;
    }
}
"""


calendar_state = st_calendar(
    events=calendar_events,
    options=calendar_options,
    custom_css=custom_css,
    key="main_calendar",
)


if isinstance(calendar_state, dict):
    callback = calendar_state.get("callback")

    if callback == "dateClick":
        date_info = calendar_state.get("dateClick", {})

        clicked_date = fix_calendar_date(
            date_info.get("date"),
            date_info.get("dateStr"),
        )

        if clicked_date and clicked_date != st.session_state["selected_date"]:
            st.session_state["selected_date"] = clicked_date
            st.rerun()

    if callback == "eventClick":
        clicked_event = calendar_state.get("eventClick", {}).get("event", {})

        clicked_start = fix_calendar_date(
            clicked_event.get("start"),
            clicked_event.get("startStr"),
        )

        if clicked_start and clicked_start != st.session_state["selected_date"]:
            st.session_state["selected_date"] = clicked_start
            st.rerun()


st.markdown('<div style="height:25px;"></div>', unsafe_allow_html=True)

sel_date_raw = datetime.strptime(st.session_state["selected_date"], "%Y-%m-%d").date()
formatted_sel_date = sel_date_raw.strftime("%d.%m.%Y")

st.markdown(
    f"""
    <div style="
        color:#8b949e;
        font-size:.85rem;
        font-weight:600;
        text-transform:uppercase;
        margin-bottom:12px;
    ">
        Plany na dzień: {formatted_sel_date}
    </div>
    """,
    unsafe_allow_html=True,
)


selected_day_events = [
    e for e in db if e["Termin"] == st.session_state["selected_date"]
]

if selected_day_events:
    for event in selected_day_events:
        c_info, c_del = st.columns([3, 1])

        with c_info:
            st.markdown(
                f"""
                <div style="padding-top:6px;">
                    <span style="color:#f0f6fc;font-weight:500;">
                        {html.escape(event["Wydarzenie"])}
                    </span>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with c_del:
            if st.button("Usuń", key=f"del_{event['id']}"):
                db.remove(event)
                st.rerun()

        st.markdown(
            '<div style="height:8px;border-bottom:1px solid #21262d;margin-bottom:8px;"></div>',
            unsafe_allow_html=True,
        )

else:
    st.markdown(
        '<div class="empty-state" style="padding:1rem;">Brak wydarzeń w tym dniu.</div>',
        unsafe_allow_html=True,
    )