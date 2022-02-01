import matplotlib.pyplot as plt

from ds_blog import db
from ds_blog.models import TimelineEntry, TimelineDelta

def td_graph_gen(character_name, id):
    td_plot = []
    entry = TimelineEntry.query.filter_by(character_name=character_name)
    entry_len = 0
    for i in entry:
        td_plot.append(i.total_deaths)
        entry_len = entry_len + 1
    x = list(range(1,(entry_len + 1)))
    y = td_plot
    plt.fill_between(x, y, color='skyblue', alpha=0.8)
    plt.plot(x, y, color='skyblue')
    plt.xlabel('Timeline Entries')
    plt.ylabel('Deaths Over Time')
    plt.savefig(f'ds_blog/static/td_graphs/{id}.jpg')

def add_new_td(character_name, total_deaths, soul_level, play_time):
    #I need to query the database for the latest entry.
    #I then need to match that entry with the most previous entry with the same character name
    #if no previous match exists, then all values that would otherwise be for the previous entry should be 0
    #finally, I need to take the values from the latest entry and subtract them from the previous entry to collect the delta of each value.
    # data = TimelineEntry.query.filter_by(character_name=character_name).first()
    data = TimelineEntry.query.filter_by(character_name=character_name).order_by(TimelineEntry.id.desc()).first()
    latest_data = TimelineEntry.query.order_by(TimelineEntry.id.desc()).first()
    try:
        last_state_deaths = int(data.total_deaths)
        print(f"last state deaths: {last_state_deaths}")
        last_state_sl = int(data.soul_level)
        print(f"last_state_sl: {last_state_sl}")
        last_state_pt = int(data.play_time)
        print(f"last_state_pt: {last_state_pt}")
    except AttributeError:
        print("couldn't pull data")
        last_state_deaths = 0
        last_state_sl = 0
        last_state_pt = 0
    try:
        last_entry_id = latest_data.id
    except AttributeError:
        print("couldn't find last entry")
        last_entry_id = 0

    tl_entry_id = last_entry_id + 1
    death_delta = total_deaths - last_state_deaths
    print(f'Death Delta {total_deaths} - {last_state_deaths} = {death_delta}')
    sl_delta = soul_level - last_state_sl
    print(f'SL Delta = {soul_level} - {last_state_sl} = {sl_delta}')
    playtime_delta = play_time - last_state_pt
    print(f"Play Time Delta= {play_time} - {last_state_pt} = {playtime_delta}")
    
    timeline_delta = TimelineDelta(
    tl_entry_id=tl_entry_id,
    death_delta=death_delta,
    sl_delta=sl_delta,
    playtime_delta=playtime_delta
    )
    db.session.add(timeline_delta)
    db.session.commit()