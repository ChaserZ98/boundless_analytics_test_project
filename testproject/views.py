import traceback
from django.shortcuts import render
from django.http import JsonResponse
from django.http import HttpResponse
from django.db import connections
import pandas as pd
import plotly.express as px
import sqlparse


def index(request) -> HttpResponse:
    return render(request, 'index.html')


def querySubmit(request) -> JsonResponse:
    cursor = None
    try:
        cursor = connections['default'].cursor()
    except Exception as e:
        responseStatus = 1
        traceback.print_exc()
        return JsonResponse(
            {
                'responseStatus': responseStatus,
                'errorDetails': str(e)
            }
        )

    zeroQuery = "select * from Moody2022_new"
    sliceQuery = str(request.POST.get('query'))

    try:
        sliceQuery = sqlparse.format(sliceQuery, reindent=True, keyword_case='upper')
        sliceQuery = sqlparse.split(sliceQuery)[0]

        cursor.execute(zeroQuery)
        rows = cursor.fetchall()

        df_zero = pd.DataFrame([ij for ij in i] for i in rows)
        df_zero.rename(
            columns={
                0: 'SCORE',
                1: 'GRADE',
                2: 'DOZES_OFF',
                3: 'TEXTING_IN_CLASS',
                4: 'PARTICIPATION'
            },
            inplace=True
        )
        df_zero['TYPE'] = "Zero"

        cursor.execute(sliceQuery)
        rows = cursor.fetchall()
        df_slice = pd.DataFrame([ij for ij in i] for i in rows)
        df_slice.rename(
            columns={
                0: 'SCORE',
                1: 'GRADE',
                2: 'DOZES_OFF',
                3: 'TEXTING_IN_CLASS',
                4: 'PARTICIPATION'
            },
            inplace=True
        )
        df_slice["TYPE"] = "Slice"

        df = pd.concat([df_zero, df_slice])

        plot = px.box(
            df,
            x='GRADE',
            y='SCORE',
            color='TYPE'
        )
        plot.update_layout(
            {
                "title": {
                    "text": "Distribution of Scores by Grade",
                    "x": 0.5
                },
                "xaxis": {
                    "title": "Letter Grade"
                },
                "yaxis": {
                    "title": "Score (out of 100)"
                }
            }
        )
        plot.update_xaxes(categoryorder="category ascending")
        plot.write_html("media/result.html")

    except Exception as e:
        responseStatus = 1
        traceback.print_exc()
        return JsonResponse({
            'responseStatus': responseStatus,
            'errorDetails': str(e)
        })

    return JsonResponse(
        {
            'query': sliceQuery
        }
    )
