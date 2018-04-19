# -*- coding: UTF-8 -*-
# Skrypt wczytujący dane o czujkach z pliku csv, przetwarzający je, a następnie zamieszczający wyniki w innym pliku csv.

import csv
import platform
import argparse
from datetime import datetime, date, timedelta


def count_sent_frames(cnt):
    if cnt[0] > cnt[-1]:
        a = max(cnt) - cnt[0] + 1
        b = cnt[-1] - min(cnt) + 1
        c = a + b
    else:
        c = max(cnt) - min(cnt) + 1

    sent_frames.append(c)


def make_control_list(cnt):
    counter_control_list = 0
    for n in range(len(cnt)):
        if n:
            counter_control_list += 1
            control_list.append(counter_control_list)

    return 0


def count_avr_delay_time(time_delta, lost_confirmations_id):
    counter_time = timedelta(seconds=0)
    for n in range(len(time_delta)):
        if n not in lost_confirmations_id:
            counter_time = counter_time + time_delta[n]

    counter_avg_time_delay = counter_time / (len(time_delta) - len(lost_confirmations_id))

    return counter_avg_time_delay


def format_time(cnt, time_string):
    for n in range(len(cnt)):
        a = datetime.strptime(time_string[n], '%H:%M:%S.%f').time()
        b = datetime.combine(date.min, a) - datetime.min
        time_datetime.append(b)

    for n in range(1, len(time_datetime)):
        c = time_datetime[n] - time_datetime[n - 1]
        if (c < timedelta(days=0)):
            c = c + timedelta(days=1)

        time_delta.append(c)

    return 0


def count_lost_frames(cnt):
    iterator_lost_frames = 0
    counter_lost_frames = 0
    for n in range(1, len(cnt)):
        if cnt[n] > cnt[n-1]:
            iterator_lost_frames = cnt[n] - cnt[n - 1] - 1
            counter_lost_frames += iterator_lost_frames
            lost_frames_list.append(iterator_lost_frames)
        elif cnt[n] == 0:
            break
        elif cnt[n] < cnt[n-1]:
            iterator_lost_frames = cnt[n] - 1
            counter_lost_frames += iterator_lost_frames
            lost_frames_list.append(iterator_lost_frames)

    lost_frames_number.append(counter_lost_frames)


def count_lost_confirmations(id0):
    counter_lost_confirmations = 0
    for n in range(1, len(id0)):
        if id0[n] == id0[n - 1]:
            counter_lost_confirmations += 1
            lost_confirmations_id.append(n - 1)

    return counter_lost_confirmations


def calc_avg_rssi(rssi):
    m = 0
    for n in range(len(rssi)):
        m += rssi[n]
    m /= len(rssi)
    # obliczenie w return wynika z dokumentacji
    return (m / 2) - 121


time_now = datetime.now().time()
time_now_str = str(time_now.strftime("%H-%M-%S"))

parser = argparse.ArgumentParser(description='Licz czujki')
parser.add_argument('-s', "--source",
                    dest="SOURCE",
                    metavar=('source_csv'),
                    required=True,
                    help="Plik wejsciowy w formacie .csv, bez wadliwych pakietow danych, \
                            obowiazkowe fieldnames: Time,DevAddr,Cnt,Id,Rssi")
parser.add_argument('-o', "--output",
                    dest="OUTPUT",
                    metavar='output_csv',
                    help="Plik wyjsciowy, np. 'output.csv'",
                    default="{0}{1}{2}".format('output_', time_now_str, '.csv'))
parser.add_argument('-d', "--delimiter",
                    dest="DELIMITER",
                    metavar='delimiter_csv',
                    required=True,
                    choices=[";", ","],
                    help="Znak specjalny w wejsciowym .csv, ktory rozdziela poszczegolne kolumny")

args = parser.parse_args()

TEN_MINUTES = 10 * 60
DevAddr = set()
all_frames = list()

with open(args.SOURCE) as csvfile:
    text = csv.DictReader(csvfile, delimiter=args.DELIMITER)
    fx = text.fieldnames
    for row in text:
        DevAddr.add(int(row['DevAddr']))
        all_frames.append(row)

sent_frames = list()
sent_confirmations = list()
expected_frames = list()
lost_frames_number = list()
max_resend_frames = list()
lost_confirmations = list()
rssi_avg = list()
avg_time_delay = list()
device_address = list()
frames_sent_to_received_ratio = list()
sensor_to_base_ratio = list()
base_to_sensor_ratio = list()
sensor_ratio = list()
base_ratio = list()
device_groups = list()

for n in range(len(DevAddr)):
    devaddr = DevAddr.pop()
    cnt = list()
    id0 = list()
    rssi = list()
    time_strings = list()

    for row in all_frames:
        if int(row['DevAddr']) == devaddr:
            cnt.append(int(row['Cnt']))
            id0.append(int(row['Id']))
            rssi.append(int(row['Rssi']))
            time_strings.append(row['Time'])

    lost_frames_list = list()
    count_lost_frames(cnt)
    max_resend_frames.append(max(lost_frames_list))

    lost_confirmations_id = list()
    counter_lost_confirmations = count_lost_confirmations(id0)
    lost_confirmations.append(counter_lost_confirmations)

    time_datetime = list()
    time_delta = list()
    format_time(cnt, time_strings)

    counter_avg_time_delay = count_avr_delay_time(time_delta, lost_confirmations_id)
    avg_time_in_seconds = counter_avg_time_delay.total_seconds() - TEN_MINUTES
    avg_time_delay.append(str(avg_time_in_seconds))

    control_list = list()
    make_control_list(cnt)

    avg_rssi = calc_avg_rssi(rssi)
    rssi_avg.append(avg_rssi)

    count_sent_frames(cnt)

    expected_frames.append(max(control_list) - min(control_list) + 1)

    device_address.append(devaddr)

    frames_sent_to_received_ratio.append(float(sent_frames[n]) / expected_frames[n])

    sensor_to_base_ratio.append((float(sent_frames[n] - lost_frames_number[n])) / sent_frames[n])

    base_to_sensor_ratio.append((float(sent_frames[n] - lost_confirmations[n])) / sent_frames[n])

    sensor_ratio.append(float(lost_frames_number[n]) / sent_frames[n])

    base_ratio.append(float(lost_confirmations[n]) / sent_frames[n])

    device_groups = [56, 121, 122, 123, 38, 52,
                     66, 32, 33, 34, 50,
                     57, 124, 125, 126, 39, 53,
                     58, 127, 0, 10, 40, 54,
                     59, 11, 12, 13, 41, 55,
                     29, 30, 31, 49,
                     60, 14, 15, 16, 44,
                     61, 17, 18, 19, 45,
                     62, 20, 21, 22, 46,
                     67, 35, 36, 37, 51,
                     64, 48,
                     63, 23, 24, 25, 47]

# print("Wyslane ramki: " + str(sent_frames))
# print("Oczekiwane ramki: " + str(expected_frames))
# print("Zgubione ramki: " + str(lost_frames_number))
# print("Max ilosc wyslanych ponownie ramek: " + str(max_resend_frames))
# print("Zgubione potwierdzenia: " + str(lost_confirmations))
# print("Rssi avg: " + str(rssi_avg))
# print("Sredni czas opoznienia " + str(avg_time_delay))
# print("Stosunek ramek wyslanych do odebranych: " + str(frames_sent_to_received_ratio))
# print("Skutecznosc baza -> czujka " + str(base_to_sensor_ratio))
# print("Skutecznosc czujka -> baza " + str(sensor_to_base_ratio))

with open(args.OUTPUT, 'w', newline='') as csvfile:
    fieldnames = ['DevAddr',
                  'Wyslane ramki',
                  'Oczekiwane ramki',
                  'Zgubione ramki',
                  'Max resend',
                  'Zgubione potwierdzenia',
                  'Rssi avg',
                  'Sredni czas opoznienia',
                  'Stosunek ramek wyslanych do odebranych',
                  'Skutecznosc baza -> czujka',
                  'Skutecznosc czujka -> baza',
                  'Procent straconych ramek',
                  'Procent straconych potwierdzen']

    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    for n in range(len(device_groups)):
        # sortpwanie wynikow po grupach w jakich zostaly rozmieszczone
        a = device_address.index(device_groups[n])
        writer.writerow(
            {'DevAddr': device_address[a],
             'Wyslane ramki': sent_frames[a],
             'Oczekiwane ramki': expected_frames[a],
             'Zgubione ramki': lost_frames_number[a],
             'Max resend': max_resend_frames[a],
             'Zgubione potwierdzenia': lost_confirmations[a],
             'Rssi avg': rssi_avg[a],
             'Sredni czas opoznienia': avg_time_delay[a],
             'Stosunek ramek wyslanych do odebranych': frames_sent_to_received_ratio[a],
             'Skutecznosc baza -> czujka': base_to_sensor_ratio[a],
             'Skutecznosc czujka -> baza': sensor_to_base_ratio[a],
             'Procent straconych ramek': sensor_ratio[a],
             'Procent straconych potwierdzen': base_ratio[a]})

version = platform.python_version()
print("Zapisano do " + args.OUTPUT)
print("Python wersja "+str(version))
