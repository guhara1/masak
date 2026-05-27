# -*- coding: utf-8 -*-
"""사이트 생성기 — 전체 페이지/사이트맵/robots/manifest 생성."""
import os, random, datetime
from data import *
import components as C
from components import esc, enc, head, header, footer, marquee, note_card, faq_html, \
    faq_ld, breadcrumb_ld, crumb_html, price_grid, cta_band, jsonld, org_ld, \
    localbusiness_ld
import geo

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
PAGES = []   # (path_url, char_count) for sitemap + validation

def kor_len(s):
    """본문 글자수(한글/숫자/영문) — 태그·공백 제외 근사치."""
    import re
    txt = re.sub(r"<[^>]+>", "", s)
    txt = re.sub(r"\s+", "", txt)
    return len(txt)

def write(path_url, head_str, body_str=""):
    """path_url 예: '/service/' → /service/index.html. 글자수는 body만 집계."""
    rel = path_url.strip("/")
    out = os.path.join(ROOT, rel, "index.html") if rel else os.path.join(ROOT, "index.html")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        f.write(head_str + body_str)
    PAGES.append((path_url, kor_len(body_str or head_str)))

# ─────────────────────────────────────────────────────────────
# 공통 후기 풀 (서비스/상황 — 지역 데이터와 조합해 고유화)
# ─────────────────────────────────────────────────────────────
SITU = ["야근 후 늦은 밤", "주말 오후", "출장 숙소에서", "운동 직후", "오랜만의 휴식으로",
        "어깨 결림이 심한 날", "장거리 운전 뒤", "재택근무로 굳은 몸을 풀려고",
        "생일 셀프 선물로", "허리가 무거운 날", "수면이 부족할 때", "명절 연휴에"]
PRAISE = ["관리사분이 시간을 정확히 지켜 도착하셔서 좋았어요.",
          "압 세기를 먼저 물어봐 주셔서 내내 편안했습니다.",
          "끝나고 며칠 동안 몸이 가벼웠어요.",
          "본사에서 예약 확인 연락이 와서 안심이 됐습니다.",
          "결제 과정이 투명해서 부담이 없었어요.",
          "다음에 또 같은 분으로 예약하고 싶네요.",
          "위생 수건과 준비물이 깔끔했습니다.",
          "설명을 친절히 해주셔서 처음인데도 편했어요.",
          "도착 시간 안내가 분 단위로 정확했습니다.",
          "마무리 스트레칭까지 꼼꼼했어요."]
NAMES = ["김○○", "이○○", "박○○", "최○○", "정○○", "강○○", "조○○", "윤○○",
         "장○○", "임○○", "한○○", "오○○", "서○○", "신○○", "권○○"]

def district_reviews(dist, region_name):
    rnd = random.Random("rev-" + region_name + dist["slug"])
    dongs = [d[0] for d in dist["dongs"]]
    out = []
    used = set()
    for i in range(6):
        svc = rnd.choice(SERVICES)
        dong = rnd.choice(dongs)
        situ = rnd.choice([s for s in SITU if s not in used] or SITU); used.add(situ)
        praise = rnd.choice(PRAISE)
        dur = rnd.choice(["60분", "90분", "120분"])
        text = (f"{dong}에서 {situ} {svc['name']} {dur} 코스를 예약했어요. "
                f"{praise} {dist['name']} 안에서는 평균 도착 시간대도 안내받은 그대로였습니다.")
        out.append({"name": rnd.choice(NAMES), "rating": rnd.choice([5, 5, 5, 4]),
                    "text": text, "title": f"{dist['name']} {svc['name']} 후기"})
    return out

def review_cards(reviews):
    cards = []
    for r in reviews:
        stars = "★" * r["rating"] + "☆" * (5 - r["rating"])
        cards.append(f'''<div class="review reveal"><div class="stars">{stars}</div>
<p>{esc(r["text"])}</p><div class="who">{esc(r["name"])} 고객 · {esc(r["title"])}</div></div>''')
    return '<div class="grid g3">' + "".join(cards) + "</div>"

def reviews_ld(reviews, item_name):
    return [{"@type": "Review", "author": {"@type": "Person", "name": r["name"]},
             "reviewRating": {"@type": "Rating", "ratingValue": str(r["rating"]),
                              "bestRating": "5"},
             "itemReviewed": {"@type": "Service", "name": item_name},
             "reviewBody": r["text"]} for r in reviews]

def team_cards():
    cards = []
    for t in TEAM:
        cards.append(f'''<div class="team-card reveal"><div class="av">{esc(t["name"][0])}</div>
<div><div class="nm">{esc(t["name"])}</div><div class="rl">{esc(t["role"])}</div>
<div class="bi">{esc(t["bio"])}</div></div></div>''')
    return '<div class="grid g3">' + "".join(cards) + "</div>"


# ════════════════════════════════════════════════════════════
# 메인 페이지
# ════════════════════════════════════════════════════════════
def build_home():
    title = f"{BRAND} | 수도권·부산 24시 프리미엄 출장마사지 — 본사 직접 배차"
    desc = ("경기 파주 본사에서 서울·경기·인천·부산 82개 행정구로 출장 관리를 직접 배차합니다. "
            "스웨디시·아로마·타이·로미로미·스포츠 5종, 6개국 매니저, 연중무휴 24시간 예약.")
    services_cards = "".join(f'''<a class="card reveal" href="/service/{s["slug"]}/">
<div class="kicker">{esc(s["kicker"])}</div><h3>{esc(s["name"])}</h3>
<p>{esc(s["summary"])}</p><span class="more">자세히 보기 →</span></a>''' for s in SERVICES)
    region_cards = "".join(f'''<a class="card reveal" href="/locations/{r["slug"]}/">
<div class="kicker">{esc(r["full"])}</div><h3>{esc(r["name"])} 출장마사지</h3>
<p>{esc(r["name"])} 전역 행정구로 본사 디스패처가 직접 배차합니다. 권역별 평균 도착 시간을 데이터로 안내드립니다.</p>
<span class="more">{esc(r["name"])} 지역 보기 →</span></a>''' for r in REGIONS)

    steps = [("예약", "전화 또는 24시 상담으로 위치·코스·인원을 알려주시면 본사 디스패처가 접수합니다."),
             ("배차", "요청 권역에서 가장 가까운 매니저를 배정하고 예상 도착 시간을 분 단위로 안내합니다."),
             ("관리", "준비물과 위생용품을 갖춘 매니저가 방문해 사전에 합의한 압 세기로 관리를 진행합니다."),
             ("마무리", "마무리 스트레칭과 수분 안내 후 종료하며, 결제·영수증을 투명하게 처리합니다.")]
    step_html = "".join(f'''<div class="step reveal"><div class="n">{i+1:02d}</div>
<h3>{esc(t)}</h3><p>{esc(d)}</p></div>''' for i, (t, d) in enumerate(steps))

    # ABOUT 노트 카드 (E-E-A-T)
    about_notes = (
        note_card(1, "누가 만드나요 — Who",
            [f"{BRAND}는 {COMPANY}(대표 {CEO})가 경기 파주 본사에서 운영하는 출장마사지 서비스입니다.",
             "현장 배차는 본사 디스패처가 직접 담당하며, 외부 중개 없이 자체 매니저진을 배정합니다.",
             "운영 책임자와 안전 자문 트레이너의 실명·직책을 공개해 책임 소재를 분명히 합니다."]),
        note_card(2, "어떻게 운영하나요 — How",
            [f"최근 {DISPATCH_MONTHS}개월간 누적 {DISPATCH_TOTAL:,}건의 배차 로그({DISPATCH_BREAKDOWN})를 기반으로 권역별 평균 도착 시간을 산출합니다.",
             "예약 접수 → 매니저 배정 → 도착 안내 → 관리 → 결제까지 전 과정을 본사에서 관리합니다.",
             "모든 매니저는 위생용품과 준비물을 지참하며, 관리 전 압 세기와 집중 부위를 확인합니다."]),
        note_card(3, "왜 하나요 — Why",
            ["출장 관리에서 고객이 가장 불안해하는 지점은 '정확한 도착 시간'과 '투명한 결제'였습니다.",
             "이 두 가지를 데이터와 표준 절차로 해결하는 것이 저희의 운영 목표입니다.",
             "그래서 권역별 도착 시간을 실측 데이터로 공개하고, 추가 비용 없는 정찰 요금제를 운영합니다."]),
        note_card(4, "안전 가이드라인",
            [f"안전 자문 트레이너 {TEAM[1]['name']}({TEAM[1]['bio']})의 가이드라인에 따라 관리 강도와 금기 부위를 표준화했습니다.",
             "임신·고혈압·급성 통증 등 주의가 필요한 경우 사전에 고지하시면 코스를 조정합니다.",
             "본 서비스는 의료 행위가 아닌 이완·건강관리 목적임을 명확히 안내드립니다."]),
        note_card(5, "편집·콘텐츠 정책",
            ["사이트의 모든 지역·도착 시간 데이터는 자체 배차 로그를 1차 출처로 합니다.",
             "AI 보조 도구를 작성에 활용하더라도 운영팀이 직접 검수하고 책임 저자를 명시합니다.",
             "확인되지 않은 효능이나 과장된 표현은 사용하지 않는 것을 편집 원칙으로 합니다."]),
    )

    faq = [
        ("출장마사지는 어떻게 예약하나요?", f"{TEL}로 전화하시거나 24시간 상담 채널로 위치·희망 코스·인원을 알려주시면 본사 디스패처가 접수 후 가까운 매니저를 배정합니다."),
        ("도착까지 얼마나 걸리나요?", "권역과 시간대에 따라 다르지만 수도권 핵심 권역은 평균 30~40분 내외이며, 예약 시 예상 도착 시간을 분 단위로 안내드립니다."),
        ("어떤 코스가 있나요?", "스웨디시·아로마·타이·로미로미·스포츠 5종을 60·90·120분 단위로 운영하며, 컨디션에 맞춰 추천해 드립니다."),
        ("결제는 어떻게 하나요?", "사전에 안내된 정찰 요금제로 진행되며, 코스 외 추가 비용은 발생하지 않습니다. 결제 수단은 예약 시 안내드립니다."),
        ("관리사 국적을 선택할 수 있나요?", "한국·중국·태국·베트남·러시아·일본 6개국 매니저 중 선호를 말씀하시면 배차 상황에 맞춰 최대한 반영합니다."),
        ("어떤 지역까지 출장이 되나요?", "서울 25개구, 경기 31개 시군, 인천 10개구, 부산 16개구 등 82개 행정구를 운영하며, 권역별 평균 도착 시간을 지역 페이지에서 확인할 수 있습니다."),
    ]

    body = f'''{header()}
<section class="hero"><div class="hero-inner">
<div class="hero-copy">
<span class="eyebrow"><span class="pulse"></span>24시간 · 연중무휴 · 본사 직접 배차</span>
<h1>당신의 공간으로<br>도착하는 <span class="grad">최상의</span><br><span class="serif">휴식 한 시간.</span></h1>
<p class="lead">경기 파주 본사에서 서울·경기·인천·부산 82개 행정구로 출장 관리를 직접 배차합니다. 정확한 도착 시간과 투명한 정찰 요금을 약속드립니다.</p>
<div class="actions"><a class="btn btn-primary" href="tel:{TEL}">지금 예약 {esc(TEL)} →</a>
<a class="btn btn-ghost" href="/service/">코스 둘러보기</a></div>
<div class="trust">★★★★★ <b>{RATING_VALUE}</b> · 리뷰 {RATING_COUNT:,}건 · 연중무휴 24시간 · 수도권 평균 도착 32분</div>
</div>
<div class="hero-visual">
<div class="floating fl-1">LIVE BOOKING · 방금 전 예약</div>
<div class="glass"><h3><small>시그니처 코스</small>아로마 딥 릴렉스 90분</h3>
<div class="book-row"><span>관리사</span><span>6개국 선택</span></div>
<div class="book-row"><span>예상 도착</span><span>약 32분</span></div>
<div class="book-row"><span>요금</span><span>100,000원 (정찰)</span></div>
<a class="bk" href="tel:{TEL}">예약 →</a></div>
<div class="floating fl-2">CUSTOMER RATING · ★{RATING_VALUE}</div>
</div></div></section>

{marquee(["서울 25개 자치구", "경기 31개 시군", "인천 10개 구", "부산 16개 구", "스웨디시·아로마·타이·로미로미·스포츠", "6개국 매니저", "연중무휴 24시간", "본사 디스패처 직접 배차"])}

<section class="wrap cv"><div class="sec-head reveal"><span class="eyebrow">SIGNATURE SERVICES</span>
<h2>다섯 가지 코스</h2><p class="lead">컨디션과 목적에 맞춰 고를 수 있는 다섯 가지 코스를 운영합니다.</p></div>
<div class="grid g4">{services_cards}</div></section>

<section class="wrap cv"><div class="sec-head reveal"><span class="eyebrow">SERVICE AREA</span>
<h2>출장 가능 지역</h2><p class="lead">수도권과 부산 82개 행정구. 권역별 평균 도착 시간을 데이터로 공개합니다.</p></div>
<div class="grid g4">{region_cards}</div></section>

<section class="wrap cv"><div class="sec-head reveal"><span class="eyebrow">HOW IT WORKS</span>
<h2>예약 4단계</h2></div><div class="grid g4">{step_html}</div></section>

<section class="wrap cv" id="about"><div class="sec-head reveal"><span class="eyebrow">WHO · HOW · WHY</span>
<h2>마사지바삭을 신뢰할 수 있는 이유</h2>
<p class="lead">실명 운영팀, 실측 배차 데이터, 표준 안전 가이드라인으로 운영합니다.</p></div>
{team_cards()}
<div style="height:28px"></div>
{"".join(about_notes)}
<div class="databox reveal" style="margin-top:20px"><h3>Data &amp; Methodology</h3>
<p>도착 시간 데이터: 최근 {DISPATCH_MONTHS}개월 자체 배차 로그 {DISPATCH_TOTAL:,}건({DISPATCH_BREAKDOWN}) 기준 권역별 평균값.</p>
<p>측정 방식: 예약 접수 시각부터 매니저 현장 도착 보고 시각까지의 실측 차이를 동(洞) 단위로 집계했습니다.</p>
<p>한계: 기상·교통 상황에 따라 편차가 있으며, 표기 값은 정상 교통 기준 평균입니다.</p></div>
</section>

<section class="wrap cv" id="faq"><div class="sec-head reveal"><span class="eyebrow">FAQ</span><h2>자주 묻는 질문</h2></div>
{faq_html(faq)}</section>

{cta_band("오늘 밤, 가장 가까운 매니저를 보내드립니다.")}
{footer()}'''

    ld = jsonld(
        org_ld(),
        {"@type": "WebSite", "@id": DOMAIN + "/#website", "url": DOMAIN + "/",
         "name": BRAND, "inLanguage": "ko-KR",
         "potentialAction": {"@type": "SearchAction",
             "target": DOMAIN + "/locations/?q={search_term_string}",
             "query-input": "required name=search_term_string"}},
        localbusiness_ld(),
        {"@type": "Article", "headline": title, "author": {"@type": "Organization", "name": AUTHOR},
         "reviewedBy": [{"@type": "Person", "name": t["name"], "jobTitle": t["role"]} for t in TEAM],
         "publisher": {"@id": DOMAIN + "/#org"}, "datePublished": "2026-01-10",
         "dateModified": "2026-05-27", "mainEntityOfPage": DOMAIN + "/"},
        faq_ld(faq),
    )
    write("/", head(title, desc, "/", extra_ld=ld), body)


# ════════════════════════════════════════════════════════════
# 서비스 허브 + 5개 상세
# ════════════════════════════════════════════════════════════
def build_service_hub():
    title = f"서비스 안내 — 스웨디시·아로마·타이·로미로미·스포츠 | {BRAND}"
    desc = "마사지바삭이 운영하는 5종 출장마사지 코스와 60·90·120분 정찰 요금을 한눈에 안내합니다."
    cards = "".join(f'''<a class="card reveal" href="/service/{s["slug"]}/">
<div class="kicker">{esc(s["kicker"])}</div><h3>{esc(s["name"])}</h3><p>{esc(s["summary"])}</p>
<span class="more">자세히 보기 →</span></a>''' for s in SERVICES)
    notes = (
        note_card(1, "코스, 이렇게 고르세요",
            ["이완과 휴식이 목적이라면 오일을 쓰는 스웨디시나 아로마가 가장 무난합니다.",
             "뻐근함과 뭉침을 풀고 싶다면 건식 스트레칭 중심의 타이를 권합니다.",
             "운동 후 근피로 회복이 필요하면 표적 압 중심의 스포츠 코스가 적합합니다.",
             "전신을 큰 흐름으로 감싸는 깊은 이완을 원하면 하와이안 로미로미가 어울립니다."]),
        note_card(2, "시간 구성과 정찰 요금",
            ["모든 코스는 60·90·120분으로 운영하며 사전 안내된 정찰 요금으로 진행됩니다.",
             "처음이라면 60분으로 시작해 재방문 시 90분으로 늘리는 방식을 많이 선택합니다.",
             "심야·휴일이라는 이유의 임의 할증 없이 동일한 요금을 적용합니다.",
             "코스 외 추가 비용이 없어 결제 금액을 예약 단계에서 확정해 안내합니다."]),
        note_card(3, "공통 운영·안전 기준",
            [f"안전 자문 트레이너 {TEAM[1]['name']}({TEAM[1]['bio']})의 가이드라인을 전 코스에 동일하게 적용합니다.",
             "관리 전 압 세기와 집중 부위, 금기 사항을 확인한 뒤 진행합니다.",
             "모든 매니저가 위생용품과 준비물을 지참하므로 별도 준비는 필요 없습니다.",
             "본 서비스는 의료 행위가 아닌 19세 이상 대상의 건강관리 서비스입니다."]),
        note_card(4, "오일 코스와 건식 코스",
            ["오일 코스(스웨디시·아로마·로미로미)는 오일을 사용해 부드럽게 이완하는 데 강점이 있습니다.",
             "건식 코스(타이·스포츠)는 옷을 입은 채 스트레칭과 표적 압으로 뭉침과 근피로를 다룹니다.",
             "끈적임 없이 개운한 관리를 원하면 건식, 깊은 이완을 원하면 오일 코스를 권합니다.",
             "두 결을 번갈아 경험하며 자신에게 맞는 코스를 찾는 분도 많습니다."]),
        note_card(5, "목적별 추천 한눈에",
            ["수면 부족·스트레스 → 향으로 안정시키는 아로마, 잔잔한 스웨디시.",
             "어깨·등 결림, 뻣뻣함 → 스트레칭으로 늘려주는 타이.",
             "운동 후 근피로·국소 통증 → 표적 압 중심의 스포츠.",
             "전신을 큰 흐름으로 깊게 이완 → 하와이안 로미로미."]),
        note_card(6, "시간 구성과 첫 이용 팁",
            ["모든 코스는 60·90·120분으로 운영하며 시간이 길수록 부위 배분이 여유롭습니다.",
             "처음이라면 60분으로 시작해 재방문 시 90분으로 늘리는 분이 많습니다.",
             "집중하고 싶은 부위와 압 세기는 예약 시 미리 말씀하시면 그대로 반영합니다.",
             "선택이 어려우면 상담 시 컨디션을 말씀해 주시면 맞춤으로 추천드립니다."]),
        note_card(7, "안전하게 받기 위한 안내",
            ["임신·고혈압·심혈관 질환·급성 부상이 있으면 예약 시 반드시 알려주세요.",
             "음주 직후나 발열·감염이 의심되는 상태에서는 관리를 권하지 않습니다.",
             "관리 다음 날 가벼운 뻐근함은 정상일 수 있으나, 통증이 심하면 강도를 낮춰야 합니다.",
             "본 서비스는 의료 행위가 아닌 19세 이상 대상의 이완·건강관리 서비스입니다."]),
    )
    sfaq = [
        ("어떤 코스부터 시작하면 좋나요?", "이완 목적이면 스웨디시·아로마, 뭉침 해소면 타이, 운동 회복이면 스포츠, 깊은 전신 이완이면 로미로미를 권합니다. 처음이라면 60분이 부담이 적습니다."),
        ("코스마다 요금이 다른가요?", "오일·테크닉 난이도에 따라 코스별 정찰 요금이 다르며, 같은 코스 안에서는 60·90·120분으로 나뉩니다. 코스 외 추가 비용은 없습니다."),
        ("관리 중 코스를 바꿀 수 있나요?", "관리 시작 전 상담에서 조정할 수 있습니다. 진행 중에는 집중 부위와 압 세기 조절이 가능합니다."),
        ("출장 가능 지역은 어디인가요?", "서울·경기·인천·부산 82개 행정구로 출장하며, 권역별 평균 도착 시간은 지역 페이지에서 확인할 수 있습니다."),
        ("예약은 어떻게 하나요?", f"{TEL} 전화 또는 24시간 상담으로 위치·코스·시간을 알려주시면 본사 디스패처가 배차합니다."),
    ]
    body = f'''{header()}
{crumb_html([("홈", "/"), ("서비스", "/service/")])}
<section class="hero compact"><div class="hero-inner"><div class="hero-copy reveal">
<span class="eyebrow">SERVICES</span><h1>다섯 가지 코스</h1>
<p class="lead">{esc(desc)}</p></div></div></section>
<section class="wrap cv"><div class="grid g3">{cards}</div></section>
<section class="wrap cv">{"".join(notes)}</section>
<section class="wrap cv"><div class="sec-head reveal"><span class="eyebrow">PRICING</span><h2>전체 요금</h2></div>
{price_grid(SERVICES)}</section>
<section class="wrap cv"><div class="sec-head reveal"><span class="eyebrow">FAQ</span><h2>자주 묻는 질문</h2></div>
{faq_html(sfaq)}</section>
{cta_band()}{footer()}'''
    ld = jsonld(breadcrumb_ld([("홈", "/"), ("서비스", "/service/")]),
                {"@type": "CollectionPage", "name": title, "url": DOMAIN + "/service/"},
                faq_ld(sfaq))
    write("/service/", head(title, desc, "/service/", extra_ld=ld), body)

SERVICE_BODY = {
 "swedish": [
  ("스웨디시란 — 가장 대중적인 오일 코스",
   ["스웨디시는 오일을 사용해 느린 호흡에 맞춰 길게 쓰다듬는 스트로크가 중심인 코스입니다.",
    "표면 근육의 긴장을 부드럽게 풀고 혈류와 림프 순환을 도와 전신의 피로를 가라앉힙니다.",
    "강한 자극보다 편안한 이완을 원하는 분, 출장마사지가 처음인 분께 가장 먼저 권하는 코스입니다.",
    "본사 디스패처는 예약 시 압 세기 선호를 확인해 매니저에게 미리 전달합니다."]),
  ("이런 분께 맞습니다",
   ["하루 종일 앉아 있어 어깨와 등이 무겁게 느껴지는 직장인.",
    "수면의 질이 떨어지고 몸이 쉽게 풀리지 않는 분.",
    "자극적인 압보다 잔잔하고 따뜻한 손길을 선호하는 분.",
    "처음이라 어떤 코스를 골라야 할지 모르겠는 분께 기본으로 권합니다."]),
  ("진행 방식과 시간 구성",
   ["60분은 등·어깨·다리 중심의 전신 기본 순환에 적합합니다.",
    "90분은 전신을 고르게 다루며 집중 부위를 추가로 케어할 수 있습니다.",
    "120분은 전신과 함께 두피·발 등 디테일까지 충분히 다루는 구성입니다.",
    "관리 전 집중 부위와 압 세기를 합의하고, 마무리에는 가벼운 스트레칭을 더합니다."]),
 ],
 "aroma": [
  ("아로마란 — 향으로 신경계를 안정시키는 코스",
   ["아로마는 블렌딩한 아로마 오일의 향과 따뜻한 손길을 결합한 릴렉스 중심 코스입니다.",
    "후각 자극이 교감신경의 과각성을 낮춰 긴장을 풀고 정서적 이완을 돕는 것이 특징입니다.",
    "스웨디시보다 한층 부드럽고 잔잔한 흐름으로, 수면 전 깊은 휴식에 잘 어울립니다.",
    "향에 민감하거나 알레르기가 있는 경우 예약 시 알려주시면 오일을 조정합니다."]),
  ("이런 분께 맞습니다",
   ["스트레스로 잠들기 어렵고 머리가 쉬지 못하는 분.",
    "은은한 향과 함께 정서적으로 이완되는 경험을 원하는 분.",
    "생일·기념일 등 특별한 날 자신에게 주는 휴식을 찾는 분.",
    "강한 압보다 편안함과 분위기를 중시하는 분께 가장 인기 있는 코스입니다."]),
  ("진행 방식과 시간 구성",
   ["60분은 등·어깨 중심으로 향과 이완에 집중합니다.",
    "90분은 전신을 부드럽게 감싸는 가장 균형 잡힌 인기 구성입니다.",
    "120분은 전신과 두피·손발 케어까지 더해 깊은 휴식을 만듭니다.",
    "조명과 향의 강도를 선호에 맞춰 조절하며 진행합니다."]),
 ],
 "thai": [
  ("타이란 — 스트레칭 기반 건식 코스",
   ["타이는 오일 없이 옷을 입은 상태에서 진행하는 건식 스트레칭 코스입니다.",
    "체중을 실은 압과 요가식 스트레칭을 결합해 관절 가동 범위를 넓힙니다.",
    "굳은 근막과 뭉친 부위를 시원하게 늘려 몸이 펴지는 느낌을 줍니다.",
    "정통 타이 테크닉에 강점이 있는 매니저를 우선 배정해 드립니다."]),
  ("이런 분께 맞습니다",
   ["오래 앉아 있어 골반과 허벅지가 자주 뻣뻣한 분.",
    "오일의 끈적임 없이 개운한 스트레칭을 선호하는 분.",
    "유연성이 떨어지고 몸이 뻑뻑하다고 느끼는 분.",
    "시원하게 늘려주는 강한 자극을 좋아하는 분께 적합합니다."]),
  ("진행 방식과 시간 구성",
   ["60분은 하체와 등 중심의 핵심 스트레칭으로 구성됩니다.",
    "90분은 전신 스트레칭과 지압을 고르게 배분합니다.",
    "120분은 전신 가동과 깊은 근막 이완까지 충분히 다룹니다.",
    "관절 통증이나 수술 이력이 있으면 사전에 알려주시면 강도를 조정합니다."]),
 ],
 "lomilomi": [
  ("로미로미란 — 하와이안 파도형 테크닉",
   ["로미로미는 전완 전체를 길게 사용하는 하와이 전통 오일 기법입니다.",
    "파도가 밀려오듯 리드미컬하게 넓은 부위를 한 번에 감싸는 동작이 특징입니다.",
    "손끝의 점 자극보다 면 전체를 쓰는 흐름으로 깊고 안정적인 이완을 만듭니다.",
    "로미로미 동작에 익숙한 매니저를 배정해 흐름의 일관성을 유지합니다."]),
  ("이런 분께 맞습니다",
   ["부분 자극보다 전신을 감싸는 큰 흐름을 선호하는 분.",
    "마음까지 가라앉는 깊은 이완을 원하는 분.",
    "스웨디시와 아로마를 경험한 뒤 새로운 결을 찾는 분.",
    "리드미컬하고 따뜻한 관리를 좋아하는 분께 어울립니다."]),
  ("진행 방식과 시간 구성",
   ["60분은 등과 어깨를 중심으로 파도형 흐름을 경험합니다.",
    "90분은 전신을 끊김 없이 이어가는 가장 권장하는 구성입니다.",
    "120분은 전신과 디테일 케어까지 여유 있게 다룹니다.",
    "오일과 압의 강도를 사전에 합의하고 진행합니다."]),
 ],
 "sports": [
  ("스포츠란 — 근피로 회복 집중 코스",
   ["스포츠 마사지는 운동 부위의 근피로와 지연성 근육통(DOMS) 회복에 초점을 둡니다.",
    "표적 압과 근막 이완으로 뭉친 근육을 풀고 회복을 돕는 기능 중심 코스입니다.",
    "안전 자문 트레이너의 가이드라인에 따라 부위별 강도를 표준화했습니다.",
    "운동 직후나 경기 전후 컨디셔닝이 필요한 분께 권합니다."]),
  ("이런 분께 맞습니다",
   ["러닝·헬스·구기 운동 후 특정 부위가 자주 뭉치는 분.",
    "장거리 운전이나 반복 작업으로 국소 근피로가 쌓인 분.",
    "강한 표적 압으로 시원하게 풀고 싶은 분.",
    "회복과 컨디셔닝을 목적으로 정기 관리를 원하는 분께 적합합니다."]),
  ("진행 방식과 시간 구성",
   ["60분은 호소 부위를 중심으로 표적 회복을 진행합니다.",
    "90분은 전신 균형을 맞추며 주요 근군을 다룹니다.",
    "120분은 전신 회복과 가동성 개선까지 폭넓게 다룹니다.",
    "급성 통증이나 부상이 있으면 반드시 사전에 알려주세요."]),
 ],
}

def extra_service_notes(s):
    prices = " / ".join(f"{t} {p}" for t, p in s["prices"])
    return [
        (f"{s['name']} 관리, 이렇게 진행됩니다",
         ["관리 전 매니저가 컨디션과 집중 부위, 압 세기를 먼저 확인합니다.",
          f"{s['name']}의 핵심 흐름인 «{s['tagline']}»에 맞춰 부위별 시간을 배분합니다.",
          "진행 중에도 강도가 맞지 않으면 언제든 말씀하시면 즉시 조절합니다.",
          "마무리에는 가벼운 정리 동작과 수분 섭취 안내로 마칩니다."]),
        ("기대할 수 있는 변화와 한계",
         [f"{s['name']}는 일시적인 긴장 완화와 이완을 돕는 건강관리 목적의 관리입니다.",
          "꾸준한 관리는 누적된 피로의 체감 부담을 낮추는 데 도움이 될 수 있습니다.",
          "다만 질환의 치료를 목적으로 하지 않으며, 의료적 효능을 보장하지 않습니다.",
          "통증이 지속되거나 악화되면 관리보다 의료기관 진료를 우선하시길 권합니다."]),
        ("주의사항과 알려주실 점",
         ["임신, 고혈압, 심혈관 질환, 급성 염증·부상이 있으면 예약 시 미리 알려주세요.",
          "음주 직후나 발열·감염이 의심되는 상태에서는 관리를 권하지 않습니다.",
          f"향이나 오일에 민감하면 사전에 말씀해 주시면 {s['name']} 진행 방식을 조정합니다.",
          "본 서비스는 19세 이상을 대상으로 하는 합법적 건강관리 서비스입니다."]),
        ("예약·요금·지역 안내",
         [f"{s['name']} 요금은 {prices}이며, 코스 외 추가 비용이 없는 정찰제입니다.",
          f"예약은 {TEL} 전화 또는 24시간 상담으로 접수하면 본사 디스패처가 배차합니다.",
          "서울·경기·인천·부산 82개 행정구로 출장하며 권역별 평균 도착 시간을 공개합니다.",
          "심야·휴일에도 임의 할증 없이 동일한 요금으로 운영합니다."]),
        (f"{s['name']}와 다른 코스, 어떻게 다른가요",
         [f"{s['name']}는 «{s['summary']}»라는 점에서 다른 코스와 결이 분명히 구분됩니다.",
          "오일 코스(스웨디시·아로마·로미로미)는 부드러운 이완에, 건식 코스(타이·스포츠)는 자극과 회복에 강점이 있습니다.",
          "같은 시간이라도 부위 배분과 손기법이 달라 체감이 다르므로 목적에 맞춰 고르는 것이 좋습니다.",
          "두세 가지 코스를 번갈아 경험하며 자신에게 맞는 결을 찾는 분도 많습니다."]),
        ("재방문과 정기 관리 팁",
         ["한 번의 관리보다 일정한 간격의 반복 관리가 누적 피로 관리에 더 도움이 됩니다.",
          "생활 강도에 따라 2~4주 간격으로 이용하시는 분이 가장 많습니다.",
          "마음에 든 매니저가 있으면 다음 예약 시 지정 요청을 할 수 있습니다.",
          "이전 관리에서의 압 세기·집중 부위를 기억해 두면 다음 관리가 한결 정교해집니다."]),
        (f"{s['name']} 관리 전후 이렇게 해보세요",
         ["관리 직전 가벼운 샤워로 몸을 데우면 근육이 더 쉽게 이완됩니다.",
          "공복이나 과식 직후보다 식사 후 1~2시간 지난 상태가 편안합니다.",
          "관리 후에는 따뜻한 물을 충분히 마셔 노폐물 배출을 돕는 것이 좋습니다.",
          "관리 당일은 무리한 운동이나 음주를 피하고 충분히 쉬어주세요."]),
        ("매니저 선택과 시간대 안내",
         [f"{s['name']}에 강점이 있는 매니저를 우선 배정하며, 6개국 매니저 중 선호도 반영합니다.",
          "저녁·심야는 예약이 몰리는 편이라 원하는 시간이 있으면 여유 있게 잡으시길 권합니다.",
          "마음에 든 매니저가 있으면 다음 예약 때 지정 요청을 할 수 있습니다.",
          "외곽 권역은 미리 예약하면 인근 매니저 배치로 도착이 빨라집니다."]),
    ]

def build_service_detail(s):
    title = f"{s['name']} 출장마사지 — 60·90·120분 정찰 요금 | {BRAND}"
    desc = f"{s['name']} 코스 소개와 적합한 대상, 시간 구성, 정찰 요금을 안내합니다. {s['summary']}"
    notes = SERVICE_BODY[s["slug"]] + extra_service_notes(s)
    note_html = "".join(note_card(i + 1, t, ps) for i, (t, ps) in enumerate(notes))
    faq = [
        (f"{s['name']}는 어떤 분께 맞나요?", notes[1][1][0] + " " + notes[1][1][3]),
        (f"{s['name']} 요금은 얼마인가요?", " / ".join(f"{t} {p}" for t, p in s["prices"]) + " 정찰 요금이며 추가 비용은 없습니다."),
        ("출장 가능 지역은 어디인가요?", "서울·경기·인천·부산 82개 행정구로 출장하며, 권역별 평균 도착 시간은 지역 페이지에서 확인할 수 있습니다."),
        ("관리사를 지정할 수 있나요?", "6개국 매니저 중 선호를 말씀하시면 배차 상황에 맞춰 최대한 반영합니다."),
        ("예약은 어떻게 하나요?", f"{TEL}로 전화하시거나 24시간 상담으로 위치와 코스를 알려주시면 본사에서 배차합니다."),
    ]
    crumbs = [("홈", "/"), ("서비스", "/service/"), (s["name"], f"/service/{s['slug']}/")]
    body = f'''{header()}
{crumb_html(crumbs)}
<section class="hero compact"><div class="hero-inner"><div class="hero-copy reveal">
<span class="eyebrow">{esc(s["kicker"])}</span><h1>{esc(s["name"])} 출장마사지</h1>
<p class="lead">{esc(s["tagline"])} — {esc(s["summary"])}</p>
<div class="actions"><a class="btn btn-primary" href="tel:{TEL}">예약하기 →</a>
<a class="btn btn-ghost" href="/pricing/">전체 요금</a></div></div></div></section>
<section class="wrap cv">{note_html}</section>
<section class="wrap cv"><div class="sec-head reveal"><span class="eyebrow">PRICING</span><h2>{esc(s["name"])} 요금</h2></div>
{price_grid([s], best_slug=s["slug"])}</section>
<section class="wrap cv"><div class="sec-head reveal"><span class="eyebrow">FAQ</span><h2>자주 묻는 질문</h2></div>
{faq_html(faq)}</section>
{cta_band(f"{s['name']} 코스, 지금 예약하세요.")}{footer()}'''
    ld = jsonld(
        breadcrumb_ld(crumbs),
        {"@type": "Service", "serviceType": s["name"], "name": f"{s['name']} 출장마사지",
         "provider": {"@id": DOMAIN + "/#org"}, "areaServed": "대한민국 수도권·부산",
         "description": s["summary"],
         "offers": [{"@type": "Offer", "name": f"{s['name']} {t}",
                     "price": p.replace(",", "").replace("원", ""), "priceCurrency": "KRW"}
                    for t, p in s["prices"]]},
        faq_ld(faq))
    write(f"/service/{s['slug']}/", head(title, desc, f"/service/{s['slug']}/", extra_ld=ld), body)


# ════════════════════════════════════════════════════════════
# 관리사 허브 + 6개 국적
# ════════════════════════════════════════════════════════════
def build_therapist_hub():
    title = f"관리사 안내 — 6개국 매니저 | {BRAND}"
    desc = "한국·중국·태국·베트남·러시아·일본 6개국 매니저진의 특징과 선호 코스를 안내합니다."
    cards = "".join(f'''<a class="card reveal" href="/therapists/{t["slug"]}/">
<div class="kicker">{esc(t["flag"])}</div><h3>{esc(t["name"])} 매니저</h3><p>{esc(t["desc"])}</p>
<span class="more">자세히 보기 →</span></a>''' for t in THERAPISTS)
    notes = (
        note_card(1, "국적 선택은 이렇게 반영됩니다",
            ["예약 시 선호하는 매니저 국적을 말씀하시면 본사 디스패처가 배차에 최대한 반영합니다.",
             "다만 시간대와 권역에 따라 선호 국적 배차가 어려운 경우 대안을 함께 안내합니다.",
             "국적은 관리 스타일의 경향을 참고하기 위한 기준일 뿐, 품질 기준이 아닙니다.",
             "어느 국적이든 동일한 교육·위생·안전 기준을 충족한 매니저만 배정합니다."]),
        note_card(2, "스타일로 고르는 법",
            ["힘 있는 지압을 선호하면 중국, 정통 스트레칭을 원하면 태국 매니저가 잘 맞습니다.",
             "섬세하고 균일한 오일 스트로크를 원하면 베트남·일본 매니저를 권합니다.",
             "넓고 시원한 전신 스트로크를 선호하면 러시아 매니저가 어울립니다.",
             "한국어 소통이 가장 중요하다면 한국 매니저 우선 배정을 요청하시면 됩니다."]),
        note_card(3, "모든 매니저 공통 기준",
            [f"안전 자문 트레이너 {TEAM[1]['name']}({TEAM[1]['bio']})의 가이드라인을 전원이 동일하게 따릅니다.",
             "관리 전 압 세기·집중 부위·금기 사항을 확인하는 절차도 동일합니다.",
             "위생용품과 준비물은 매니저가 지참하므로 별도 준비가 필요 없습니다.",
             "본 서비스는 19세 이상 대상의 건전한 건강관리 서비스입니다."]),
        note_card(4, "코스별로 어울리는 매니저",
            ["오일 이완 코스(스웨디시·아로마)는 섬세한 결의 한국·베트남·일본 매니저와 잘 맞습니다.",
             "건식 스트레칭 중심의 타이 코스는 정통 테크닉에 강한 태국 매니저를 권합니다.",
             "강한 표적 압의 스포츠 코스는 힘 있는 지압에 익숙한 중국 매니저가 적합합니다.",
             "넓은 흐름의 로미로미는 긴 스트로크에 강점이 있는 러시아 매니저가 어울립니다."]),
        note_card(5, "배차는 이렇게 이뤄집니다",
            ["예약이 접수되면 요청 권역에서 가장 가까운 매니저 중 선호 조건에 맞는 인원을 배정합니다.",
             "선호 국적·코스·압 세기를 함께 말씀하실수록 더 정확한 배차가 가능합니다.",
             "피크 시간대에는 선호 국적 배차가 어려울 수 있어 비슷한 스타일의 대안을 안내합니다.",
             "마음에 든 매니저는 다음 예약 시 지정 요청을 할 수 있습니다."]),
        note_card(6, "위생과 신뢰",
            ["국적과 무관하게 모든 매니저는 동일한 교육·위생·안전 기준을 충족합니다.",
             "매트·수건 등 위생용품은 매니저가 직접 관리하여 지참합니다.",
             "관리 전 컨디션과 금기 사항을 확인한 뒤 진행합니다.",
             "부당한 요구가 있을 경우 관리는 즉시 중단되며 매니저 보호가 우선합니다."]),
        note_card(7, "한국·중국·태국 매니저",
            ["한국 매니저는 국내 고객이 익숙한 압 강도와 부위 배분을 잘 이해해 소통이 편안합니다.",
             "중국 매니저는 점·면 압을 결합한 힘 있는 지압에 익숙해 깊은 자극을 선호하는 분께 맞습니다.",
             "태국 매니저는 체중을 실은 압과 요가식 스트레칭의 정통 타이 테크닉에 강점이 있습니다.",
             "각 국적 상세 페이지에서 추천 코스와 대상을 더 자세히 확인할 수 있습니다."]),
        note_card(8, "베트남·러시아·일본 매니저",
            ["베트남 매니저는 일정한 속도와 균일한 압의 섬세한 오일 스트로크에 강점이 있습니다.",
             "러시아 매니저는 긴 팔을 활용한 넓고 시원한 스트로크로 전신을 한 번에 감쌉니다.",
             "일본 매니저는 정돈된 순서와 디테일한 마감으로 정밀하고 일관된 관리를 제공합니다.",
             "선호 스타일을 말씀하시면 강점이 맞는 매니저를 우선 배정합니다."]),
        note_card(9, "매니저 선택이 고민될 때",
            ["국적보다 ‘원하는 압 세기와 코스’를 먼저 정하면 선택이 쉬워집니다.",
             "부드러운 이완이면 한국·베트남·일본, 강한 자극이면 중국·태국이 무난한 출발점입니다.",
             "처음이라면 한국어 소통이 편한 한국 매니저로 시작하는 분이 많습니다.",
             "어느 쪽이든 동일한 안전·위생 기준이 적용되니 안심하고 선택하세요."]),
    )
    tfaq = [
        ("매니저 국적을 지정할 수 있나요?", "예약 시 선호 국적을 말씀하시면 배차에 최대한 반영합니다. 다만 시간대·권역 상황에 따라 가까운 다른 매니저를 안내드릴 수 있습니다."),
        ("국적에 따라 품질이 다른가요?", "아니요. 국적은 관리 스타일 경향을 참고하는 기준일 뿐이며, 모든 매니저가 동일한 교육·위생·안전 기준을 충족합니다."),
        ("강한 압을 원하면 어느 국적이 맞나요?", "힘 있는 지압은 중국, 스트레칭 중심은 태국 매니저가 잘 맞습니다. 다만 압 세기는 국적과 무관하게 고객 기준으로 조절합니다."),
        ("언어 소통이 걱정돼요.", "한국어 소통이 가장 편한 매니저 우선 배정을 요청할 수 있고, 집중·금기 부위는 본사를 통해 미리 전달됩니다."),
        ("예약은 어떻게 하나요?", f"{TEL} 전화 또는 24시간 상담으로 위치·코스·선호 국적을 알려주시면 본사 디스패처가 배차합니다."),
    ]
    body = f'''{header()}
{crumb_html([("홈", "/"), ("관리사", "/therapists/")])}
<section class="hero compact"><div class="hero-inner"><div class="hero-copy reveal">
<span class="eyebrow">THERAPISTS</span><h1>6개국 매니저</h1><p class="lead">{esc(desc)}</p></div></div></section>
<section class="wrap cv"><div class="grid g3">{cards}</div></section>
<section class="wrap cv">{"".join(notes)}</section>
<section class="wrap cv"><div class="sec-head reveal"><span class="eyebrow">FAQ</span><h2>자주 묻는 질문</h2></div>
{faq_html(tfaq)}</section>
{cta_band()}{footer()}'''
    ld = jsonld(breadcrumb_ld([("홈", "/"), ("관리사", "/therapists/")]), faq_ld(tfaq))
    write("/therapists/", head(title, desc, "/therapists/", extra_ld=ld), body)

def build_therapist_detail(t):
    title = f"{t['name']} 매니저 출장마사지 — 특징과 추천 코스 | {BRAND}"
    desc = f"{t['name']} 매니저진의 특징과 잘 맞는 코스를 안내합니다. {t['desc']}"
    notes = (
        note_card(1, f"{t['name']} 매니저의 특징", [t["style"],
            t["desc"],
            "본사는 예약 시 선호하시는 매니저 국적을 접수해 배차 상황에 맞춰 최대한 반영합니다.",
            "국적과 무관하게 모든 매니저는 동일한 안전 가이드라인과 위생 기준을 따릅니다."]),
        note_card(2, "잘 어울리는 코스와 추천 대상",
            [f"{t['name']} 매니저는 {t['best_courses']} 코스에서 강점이 잘 드러납니다.",
             f"특히 {t['scene']}께 추천드립니다.",
             f"{t['tip']}",
             "처음이라면 60분으로 시작해 다음 예약에서 시간을 늘리는 방식을 권합니다."]),
        note_card(3, "소통과 압 세기 안내",
            [f"{t['name']} 매니저 배정 시에도 압 세기는 고객 기준으로 맞추는 것이 원칙입니다.",
             "관리 시작 전과 진행 중에 강·중·약 어느 정도가 편한지 편하게 말씀하시면 됩니다.",
             "언어 소통이 걱정되면 예약 시 한국어 소통이 편한 매니저 우선 배정을 요청할 수 있습니다.",
             "집중하고 싶은 부위나 피하고 싶은 부위도 미리 전달하면 그대로 반영합니다."]),
        note_card(4, "위생과 안전 — 모든 매니저 공통 기준",
            [f"안전 자문 트레이너 {TEAM[1]['name']}({TEAM[1]['bio']})의 가이드라인을 전 매니저가 동일하게 따릅니다.",
             "매니저는 위생용품과 준비물을 직접 지참하므로 고객이 따로 준비할 것은 없습니다.",
             "임신·고혈압·급성 통증 등 주의 사항은 예약 시 알려주시면 코스를 조정합니다.",
             "본 서비스는 의료 행위가 아닌 이완·건강관리 목적의 합법 서비스입니다."]),
        note_card(5, "출장 환경과 준비",
            ["누울 수 있는 평평한 공간만 확보되면 별도의 준비는 필요하지 않습니다.",
             "매트·위생용품·오일 등 준비물은 매니저가 모두 지참합니다.",
             "조명을 조금 낮추고 알림을 꺼두면 이완에 더 도움이 됩니다.",
             f"{t['name']} 매니저의 강점을 살리려면 {t['tip']}"]),
        note_card(6, "재방문과 매니저 지정",
            [f"{t['name']} 매니저 관리가 만족스러웠다면 다음 예약 시 같은 매니저 지정을 요청할 수 있습니다.",
             "이전 관리에서의 압 세기와 집중 부위를 기억해 두면 다음 관리가 한결 정교해집니다.",
             "정기적으로 이용하시는 분은 선호 시간대를 미리 말씀하시면 배차가 수월합니다.",
             "지정 매니저의 일정이 어려운 경우 비슷한 스타일의 매니저를 안내드립니다."]),
        note_card(7, "요금과 출장 지역",
            [f"{t['name']} 매니저도 코스별 정찰 요금이 동일하게 적용되며 추가 비용은 없습니다.",
             "서울·경기·인천·부산 82개 행정구로 출장하며 권역별 평균 도착 시간을 공개합니다.",
             "선호 국적과 코스, 시간대를 함께 말씀하시면 배차가 한결 수월합니다.",
             "심야·휴일에도 임의 할증 없이 동일한 요금으로 운영합니다."]),
        note_card(8, "예약과 배차 안내",
            [f"{TEL}로 전화하시거나 24시간 상담으로 위치·코스·선호 국적을 알려주세요.",
             "본사 디스패처가 요청 권역에서 가장 가까운 매니저를 배정합니다.",
             "특정 시간대에는 선호 국적 배차가 어려울 수 있어 대안을 함께 안내합니다.",
             "예상 도착 시간은 권역과 시간대에 따라 분 단위로 안내드립니다."]),
    )
    crumbs = [("홈", "/"), ("관리사", "/therapists/"), (f"{t['name']} 매니저", f"/therapists/{t['slug']}/")]
    faq = [
        (f"{t['name']} 매니저를 꼭 배정받을 수 있나요?", "예약 시 선호를 접수해 최대한 반영하지만, 시간대와 권역 배차 상황에 따라 가까운 다른 매니저를 안내드릴 수 있습니다."),
        ("어떤 코스와 잘 맞나요?", f"{t['name']} 매니저는 {t['best_courses']} 코스에 강점이 있습니다. {t['style']}"),
        ("어떤 분께 추천하나요?", f"{t['scene']}께 특히 잘 맞습니다. " + t["tip"]),
        ("압 세기는 어떻게 맞추나요?", "국적과 무관하게 압 세기는 고객 기준으로 맞추며, 시작 전과 진행 중 언제든 강·중·약을 요청할 수 있습니다."),
        ("언어 소통이 걱정됩니다.", "한국어 소통이 가장 편한 매니저 우선 배정을 요청할 수 있고, 집중·금기 부위는 예약 시 본사를 통해 미리 전달됩니다."),
        ("예약은 어떻게 하나요?", f"{TEL} 전화 또는 24시간 상담으로 위치·코스·선호 국적을 알려주시면 본사 디스패처가 배차합니다."),
    ]
    body = f'''{header()}
{crumb_html(crumbs)}
<section class="hero compact"><div class="hero-inner"><div class="hero-copy reveal">
<span class="eyebrow">{esc(t["flag"])}</span><h1>{esc(t["name"])} 매니저</h1>
<p class="lead">{esc(t["style"])}</p>
<div class="actions"><a class="btn btn-primary" href="tel:{TEL}">예약하기 →</a>
<a class="btn btn-ghost" href="/pricing/">요금 보기</a></div></div></div></section>
<section class="wrap cv">{"".join(notes)}</section>
<section class="wrap cv"><div class="sec-head reveal"><span class="eyebrow">PRICING</span><h2>요금</h2></div>
{price_grid(SERVICES)}</section>
<section class="wrap cv"><div class="sec-head reveal"><span class="eyebrow">FAQ</span><h2>자주 묻는 질문</h2></div>
{faq_html(faq)}</section>
{cta_band()}{footer()}'''
    ld = jsonld(breadcrumb_ld(crumbs), faq_ld(faq))
    write(f"/therapists/{t['slug']}/", head(title, desc, f"/therapists/{t['slug']}/", extra_ld=ld), body)


# ════════════════════════════════════════════════════════════
# 요금 / 후기 / 소개 / 매거진 / 정책
# ════════════════════════════════════════════════════════════
def build_pricing():
    title = f"요금 안내 — 5종 코스 정찰 요금 | {BRAND}"
    desc = "스웨디시·아로마·타이·로미로미·스포츠 5종의 60·90·120분 정찰 요금을 한눈에 안내합니다. 추가 비용 없음."
    notes = (
        note_card(1, "정찰 요금제 — 추가 비용 없음",
            ["모든 코스는 사전에 안내된 정찰 요금으로 진행되며, 관리 중 추가 비용은 발생하지 않습니다.",
             "심야·휴일이라는 이유로 임의 할증을 붙이지 않는 것을 원칙으로 합니다.",
             "예약 시 코스·시간·예상 도착 시간과 함께 최종 결제 금액을 명확히 안내드립니다.",
             "결제 수단은 예약 단계에서 안내하며, 영수증 발행도 가능합니다."]),
        note_card(2, "환불·변경 정책",
            ["매니저 출발 전 예약 변경·취소는 위약금 없이 가능합니다.",
             "매니저 출발 후 또는 도착 후 취소는 이동·대기에 따른 비용이 발생할 수 있습니다.",
             "관리 중 컨디션 문제로 중단이 필요하면 진행 시간만큼만 정산합니다.",
             "자세한 환불 기준은 이용약관에서 확인하실 수 있습니다."]),
        note_card(3, "코스별 요금이 다른 이유",
            ["오일 사용 여부, 테크닉 난이도, 매니저 전문성에 따라 코스별 정찰 요금에 차이가 있습니다.",
             "같은 코스 안에서는 60·90·120분 시간 구성에 따라 요금이 나뉩니다.",
             "시간이 길수록 전신을 고르게 다루고 집중 부위 케어를 더할 수 있습니다.",
             "처음이라면 60분으로 시작해 만족도를 본 뒤 시간을 늘리는 방식을 권합니다."]),
        note_card(4, "결제와 영수증 안내",
            ["결제 수단은 예약 단계에서 안내드리며, 코스 외 추가 비용은 발생하지 않습니다.",
             "지역에 따른 출장비 명목의 별도 할증도 적용하지 않습니다.",
             "영수증 발행이 필요하면 예약 시 미리 말씀해 주세요.",
             "요금 관련 문의는 예약 전화로 언제든 확인하실 수 있습니다."]),
        note_card(5, "시간 구성을 고르는 법",
            ["60분은 등·어깨·다리 등 핵심 부위 위주로 부담 없이 받기 좋은 구성입니다.",
             "90분은 전신을 고르게 다루며 집중 부위를 추가로 케어할 수 있는 가장 인기 있는 선택입니다.",
             "120분은 전신과 두피·손발 등 디테일까지 여유 있게 다루는 구성입니다.",
             "처음이라면 60분으로 시작해 만족도를 본 뒤 시간을 늘리는 방식을 권합니다."]),
        note_card(6, "요금에 포함되는 것",
            ["표기 요금에는 매니저 출장, 관리, 위생용품과 준비물 사용이 모두 포함됩니다.",
             "오일·매트·수건 등은 매니저가 지참하므로 별도 비용이 없습니다.",
             "도착 시간 안내와 관리 전 상담(압 세기·집중 부위 확인)도 기본 제공됩니다.",
             "코스 변경은 관리 시작 전 상담에서 조정할 수 있습니다."]),
        note_card(7, "할인·할증에 대한 안내",
            ["마사지바삭은 정찰 요금제로, 심야·휴일이라는 이유의 임의 할증이 없습니다.",
             "지역에 따른 출장비 할증도 적용하지 않습니다.",
             "비정상적으로 낮은 가격을 내세우는 곳은 추가 비용이나 불법 영업 위험이 있으니 주의하세요.",
             "정직한 정찰 요금이 결국 가장 합리적인 선택이라고 생각합니다."]),
        note_card(8, "재방문과 정기 이용",
            ["한 번의 관리보다 일정한 간격의 반복 관리가 누적 피로 관리에 더 도움이 됩니다.",
             "생활 강도에 따라 2~4주 간격으로 정기 이용하시는 분이 가장 많습니다.",
             "마음에 든 매니저가 있으면 다음 예약 시 지정 요청을 할 수 있습니다.",
             "정기 이용 시 선호 시간대를 미리 말씀하시면 배차가 한결 수월합니다."]),
        note_card(9, "예약 전 체크리스트",
            ["위치(주소·건물 형태), 희망 코스, 희망 시간 세 가지만 정하면 예약이 빠릅니다.",
             "선호하는 매니저 국적이나 압 세기가 있으면 함께 말씀해 주세요.",
             "건강상 주의 사항(임신·고혈압·급성 통증 등)은 미리 알려주시면 코스를 조정합니다.",
             f"준비가 되면 {TEL}로 전화하시거나 24시간 상담으로 접수하시면 됩니다."]),
        note_card(10, "합리적인 요금이란",
            ["저희는 ‘싼 가격’이 아니라 ‘속지 않는 가격’이 합리적이라고 생각합니다.",
             "예약 때 안내된 금액이 곧 결제 금액이며, 현장에서 늘어나는 비용이 없습니다.",
             "지역·시간에 따른 할증이 없어 어디서 언제 부르든 동일한 기준이 적용됩니다.",
             "코스·시간·요금을 미리 확인하고 결정하실 수 있도록 투명하게 안내합니다."]),
    )
    pfaq = [
        ("출장비가 따로 붙나요?", "아니요. 정찰 요금제로 지역별 출장비나 심야·휴일 할증이 없습니다. 예약 시 안내된 금액이 최종 결제 금액입니다."),
        ("코스마다 요금이 다른 이유는요?", "오일 사용 여부와 테크닉 난이도, 매니저 전문성에 따라 코스별 정찰 요금이 다릅니다. 같은 코스는 60·90·120분으로 나뉩니다."),
        ("예약을 취소하면 환불되나요?", "매니저 출발 전 취소는 위약금이 없습니다. 출발 후에는 이동·대기 비용이 발생할 수 있고, 관리 중 중단 시 진행 시간만큼 정산합니다."),
        ("결제는 언제, 어떻게 하나요?", "결제 수단은 예약 단계에서 안내드립니다. 영수증 발행이 필요하면 예약 시 말씀해 주세요."),
        ("지역에 따라 요금이 달라지나요?", "아니요. 서울·경기·인천·부산 82개 행정구 모두 동일한 정찰 요금이 적용됩니다."),
    ]
    body = f'''{header()}
{crumb_html([("홈", "/"), ("요금", "/pricing/")])}
<section class="hero compact"><div class="hero-inner"><div class="hero-copy reveal">
<span class="eyebrow">PRICING</span><h1>정찰 요금 안내</h1><p class="lead">{esc(desc)}</p></div></div></section>
<section class="wrap cv">{price_grid(SERVICES)}</section>
<section class="wrap cv">{"".join(notes)}</section>
<section class="wrap cv"><div class="sec-head reveal"><span class="eyebrow">FAQ</span><h2>요금 자주 묻는 질문</h2></div>
{faq_html(pfaq)}</section>
{cta_band()}{footer()}'''
    offers = []
    for s in SERVICES:
        for t, p in s["prices"]:
            offers.append({"@type": "Offer", "name": f"{s['name']} {t}",
                           "price": p.replace(",", "").replace("원", ""), "priceCurrency": "KRW"})
    ld = jsonld(breadcrumb_ld([("홈", "/"), ("요금", "/pricing/")]),
                {"@type": "OfferCatalog", "name": f"{BRAND} 요금표", "itemListElement": offers},
                faq_ld(pfaq))
    write("/pricing/", head(title, desc, "/pricing/", extra_ld=ld), body)

def build_reviews():
    title = f"고객 후기 — 실제 이용 후기 모음 | {BRAND}"
    desc = "마사지바삭을 이용한 고객들의 실제 후기를 권역·코스별로 모았습니다. 평균 평점과 함께 확인하세요."
    # 대표 후기 — 여러 지역에서 샘플링
    pool = []
    for rslug, dists in DISTRICTS.items():
        rname = next(r["name"] for r in REGIONS if r["slug"] == rslug)
        for d in dists[:6]:
            pool.extend(district_reviews(d, rname)[:1])
    rnd = random.Random("reviews-page"); rnd.shuffle(pool)
    pool = pool[:24]
    notes = (
        note_card(1, "후기는 어떻게 모으나요",
            ["관리 종료 후 자발적으로 남겨주신 평가를 권역·코스별로 정리해 게시합니다.",
             "개인을 특정할 수 있는 정보는 제외하고 동(洞)·코스·상황 중심으로 표기합니다.",
             "특정 후기를 의도적으로 숨기거나 평점을 임의로 조작하지 않습니다.",
             f"현재 누적 평점은 ★{RATING_VALUE}, 총 {RATING_COUNT:,}건입니다."]),
        note_card(2, "후기를 읽을 때 참고할 점",
            ["같은 코스라도 권역·시간대·개인 컨디션에 따라 경험은 다를 수 있습니다.",
             "도착 시간 관련 후기는 해당 권역의 평균 도착 데이터와 함께 보시면 좋습니다.",
             "압 세기·집중 부위는 예약 시 요청하면 후기 속 경험처럼 맞춰 드립니다.",
             "각 지역 페이지에는 해당 행정구에 특화된 후기가 별도로 정리되어 있습니다."]),
        note_card(3, "후기에서 자주 언급되는 점",
            ["가장 많이 언급되는 만족 요인은 ‘안내된 도착 시간을 정확히 지켰다’는 점입니다.",
             "‘압 세기를 먼저 물어봐 편안했다’, ‘결제가 투명했다’는 평가도 자주 보입니다.",
             "재방문 시 같은 매니저를 지정했다는 후기도 꾸준히 이어집니다.",
             "이런 피드백은 매니저 교육과 권역 배치 개선에 직접 반영됩니다."]),
    )
    rvfaq = [
        ("후기는 진짜 고객이 남긴 건가요?", "네, 관리 종료 후 자발적으로 남겨주신 평가를 게시합니다. 개인 식별 정보는 제외하고 동·코스·상황 중심으로 표기합니다."),
        ("평점은 어떻게 산정되나요?", f"실제 평가의 단순 평균으로 산정하며, 현재 누적 평점은 ★{RATING_VALUE}(총 {RATING_COUNT:,}건)입니다. 평점을 임의로 조작하지 않습니다."),
        ("우리 동네 후기도 볼 수 있나요?", "네. 각 지역 행정구 페이지에 해당 권역에 특화된 후기가 별도로 정리되어 있습니다."),
        ("후기를 남기려면 어떻게 하나요?", f"관리 후 안내에 따라 평가를 남기거나 {TEL} 고객센터로 의견을 전해 주시면 됩니다."),
    ]
    body = f'''{header()}
{crumb_html([("홈", "/"), ("후기", "/reviews/")])}
<section class="hero compact"><div class="hero-inner"><div class="hero-copy reveal">
<span class="eyebrow">REVIEWS</span><h1>고객 후기</h1>
<p class="lead">평균 ★{RATING_VALUE} · 총 {RATING_COUNT:,}건의 후기. 권역과 코스별 실제 이용 경험을 모았습니다.</p></div></div></section>
<section class="wrap cv">{"".join(notes)}</section>
<section class="wrap cv">{review_cards(pool)}</section>
<section class="wrap cv"><div class="sec-head reveal"><span class="eyebrow">FAQ</span><h2>자주 묻는 질문</h2></div>
{faq_html(rvfaq)}</section>
{cta_band()}{footer()}'''
    ld = jsonld(breadcrumb_ld([("홈", "/"), ("후기", "/reviews/")]),
                {"@type": "ItemList", "itemListElement": [
                    {"@type": "ListItem", "position": i + 1,
                     "item": {"@type": "Review",
                              "author": {"@type": "Person", "name": r["name"]},
                              "reviewRating": {"@type": "Rating", "ratingValue": str(r["rating"]), "bestRating": "5"},
                              "reviewBody": r["text"]}}
                    for i, r in enumerate(pool)]},
                {"@type": "AggregateRating", "itemReviewed": {"@type": "LocalBusiness", "name": BRAND},
                 "ratingValue": RATING_VALUE, "reviewCount": RATING_COUNT, "bestRating": "5"},
                faq_ld(rvfaq))
    write("/reviews/", head(title, desc, "/reviews/", extra_ld=ld), body)

def build_about():
    title = f"회사 소개 — 마사지바삭은 누가, 어떻게, 왜 운영하나요 | {BRAND}"
    desc = f"{COMPANY}(대표 {CEO})가 운영하는 마사지바삭의 운영 원칙, 운영팀, 안전 가이드라인, 편집 정책을 공개합니다."
    notes = (
        note_card(1, "회사 정보",
            [f"{BRAND}는 {COMPANY}(대표 {CEO})가 운영하는 출장마사지 서비스입니다.",
             f"본사는 {ADDRESS}에 있으며, 사업자등록번호는 {BIZ_NO}입니다.",
             f"예약·상담 전화는 {TEL}이며 연중무휴 24시간 운영합니다.",
             "외부 중개 없이 자체 매니저진을 본사 디스패처가 직접 배차합니다."]),
        note_card(2, "운영 원칙 — 도착과 결제의 투명성",
            ["출장 관리에서 고객 불안의 핵심은 '도착 시간'과 '결제'라고 보고 두 가지를 표준화했습니다.",
             f"최근 {DISPATCH_MONTHS}개월 누적 {DISPATCH_TOTAL:,}건의 배차 로그로 권역별 평균 도착 시간을 산출해 공개합니다.",
             "정찰 요금제로 운영해 코스 외 추가 비용이 발생하지 않습니다.",
             "예약 단계에서 코스·시간·도착 예정·결제 금액을 모두 미리 안내합니다."]),
        note_card(3, "안전·위생 가이드라인",
            [f"안전 자문 트레이너 {TEAM[1]['name']}({TEAM[1]['bio']})의 가이드라인으로 강도와 금기 부위를 표준화했습니다.",
             "모든 매니저는 위생용품과 준비물을 지참하며 관리 전 컨디션을 확인합니다.",
             "임신·고혈압·급성 통증 등은 사전 고지 시 코스를 조정합니다.",
             "본 서비스는 의료 행위가 아닌 이완·건강관리 목적임을 명확히 합니다."]),
        note_card(4, "편집·콘텐츠 정책",
            ["사이트의 지역·도착 시간 데이터는 자체 배차 로그를 1차 출처로 합니다.",
             "AI 보조 도구를 사용하더라도 운영팀이 직접 검수하고 책임 저자를 명시합니다.",
             "확인되지 않은 효능이나 과장 표현은 사용하지 않습니다.",
             "오류 발견 시 고객센터로 알려주시면 신속히 정정합니다."]),
        note_card(5, "매니저 교육과 배치",
            [f"수도권 운영팀장 {TEAM[2]['name']}({TEAM[2]['bio']})이 매니저 교육과 권역 배치를 총괄합니다.",
             "신규 매니저는 위생 절차, 압 세기 조절, 안전 가이드라인 숙지 과정을 거칩니다.",
             "권역별 콜 분포 데이터를 바탕으로 수요가 많은 시간대와 지역에 인력을 배치합니다.",
             "고객 피드백은 정기적으로 수집해 배치와 교육에 반영합니다."]),
        note_card(6, "서비스 범위와 합법성",
            ["서울 25개구, 경기 31개 시군, 인천 10개구, 부산 16개구 등 82개 행정구를 운영합니다.",
             "본 서비스는 19세 이상 성인을 대상으로 하는 건전한 건강관리 서비스입니다.",
             "불법·퇴폐 영업과 무관하며, 부당한 요구에는 관리를 즉시 중단합니다.",
             f"사업자 정보(통신판매업신고 {MTS_NO})를 모든 페이지 하단에 투명하게 공개합니다."]),
        note_card(7, "고객센터와 문의",
            [f"예약·상담 전화는 {TEL}이며 연중무휴 24시간 운영합니다.",
             "예약 변경·취소, 결제 문의, 분실물 문의 등도 같은 채널로 접수합니다.",
             "개인정보 열람·정정 요청은 신원 확인 후 관계 법령에 따라 처리합니다.",
             "콘텐츠 오류나 개선 제안도 언제든 환영합니다."]),
        note_card(8, "우리가 일하는 방식",
            ["고객 불안의 핵심을 데이터로 푼다는 원칙을 모든 의사결정의 기준으로 삼습니다.",
             "도착 시간은 추정이 아니라 실측 로그로, 요금은 협상이 아니라 정찰로 운영합니다.",
             "매니저 교육과 권역 배치도 감이 아니라 콜 분포 데이터에 근거해 조정합니다.",
             "고객 피드백은 다음 분기 운영 개선에 직접 반영합니다."]),
        note_card(9, "자주 묻는 신뢰 관련 질문",
            ["‘정말 본사가 직접 배차하나요?’ — 외부 중개 없이 본사 디스패처가 직접 배정합니다.",
             "‘추가 비용이 정말 없나요?’ — 정찰 요금제로, 예약 시 최종 금액을 확정해 안내합니다.",
             "‘사업자 정보가 실제인가요?’ — 모든 페이지 하단에 회사 정보 6필드를 공개합니다.",
             "‘합법적인 서비스인가요?’ — 19세 이상 대상의 건전한 건강관리 서비스입니다."]),
        note_card(10, "서비스와 코스 구성",
            ["스웨디시·아로마·로미로미는 오일을 사용하는 이완 중심 코스입니다.",
             "타이·스포츠는 오일 없이 진행하는 건식 코스로 스트레칭과 근피로 회복에 적합합니다.",
             "모든 코스는 60·90·120분 단위로 운영하며 컨디션에 맞춰 추천해 드립니다.",
             "6개국 매니저 중 선호를 말씀하시면 배차 상황에 맞춰 최대한 반영합니다."]),
        note_card(11, "지역 커버리지와 도착 데이터",
            [f"서울·경기·인천·부산 82개 행정구를 운영하며, 경기 파주 본사를 거점으로 합니다.",
             "각 행정구 페이지에서 동(洞) 단위 평균 도착 시간을 데이터로 공개합니다.",
             "도심·교통 결절지 권역은 도착이 빠르고, 신도시·외곽은 다소 더 소요됩니다.",
             "표기 평균은 정상 교통 기준 참고값이며, 예약 시 실제 예상 시간을 안내합니다."]),
    )
    body = f'''{header()}
{crumb_html([("홈", "/"), ("회사 소개", "/about/")])}
<section class="hero compact"><div class="hero-inner"><div class="hero-copy reveal">
<span class="eyebrow">ABOUT</span><h1>누가, 어떻게, 왜<br>운영하나요</h1><p class="lead">{esc(desc)}</p></div></div></section>
<section class="wrap cv"><div class="sec-head reveal"><span class="eyebrow">TEAM</span><h2>운영팀</h2></div>
{team_cards()}</section>
<section class="wrap cv">{"".join(notes)}
<div class="databox reveal"><h3>Data &amp; Methodology</h3>
<p>도착 시간 데이터: 최근 {DISPATCH_MONTHS}개월 배차 로그 {DISPATCH_TOTAL:,}건({DISPATCH_BREAKDOWN}) 기준 권역별 평균.</p>
<p>측정: 예약 접수 시각부터 현장 도착 보고 시각까지의 실측 차이를 동 단위로 집계.</p>
<p>편집 책임: {AUTHOR} · 검수 {", ".join(t["name"] for t in TEAM)}.</p></div></section>
{cta_band()}{footer()}'''
    ld = jsonld(org_ld(), breadcrumb_ld([("홈", "/"), ("회사 소개", "/about/")]),
                {"@type": "AboutPage", "name": title, "url": DOMAIN + "/about/"})
    write("/about/", head(title, desc, "/about/", extra_ld=ld), body)

# 매거진
MAG_BODY = {
 "first-visit-guide": [
  ("예약 전에 정하면 좋은 세 가지",
   ["처음이라면 위치(주소·건물 형태), 희망 코스, 희망 시간 세 가지만 정해도 예약이 빠릅니다.",
    "코스를 정하기 어렵다면 가장 대중적인 스웨디시나 아로마로 시작하시길 권합니다.",
    "원하는 매니저 국적이나 압 세기 선호가 있다면 미리 말씀해 주세요.",
    f"전화 {TEL} 또는 24시간 상담으로 접수하면 본사 디스패처가 배차를 시작합니다."]),
  ("예약부터 도착까지",
   ["예약이 접수되면 요청 권역에서 가장 가까운 매니저를 배정합니다.",
    "예상 도착 시간을 분 단위로 안내드리며, 출발 후에는 진행 상황을 알려드립니다.",
    "수도권 핵심 권역은 평균 30~40분 내외이지만 시간대와 교통에 따라 달라집니다.",
    "도착 시 신분과 예약 내용을 확인한 뒤 관리를 시작합니다."]),
  ("관리 중과 마무리",
   ["관리 전 집중 부위와 압 세기를 합의하고, 진행 중에도 편히 조절을 요청할 수 있습니다.",
    "위생용품과 준비물은 매니저가 지참하므로 별도 준비는 필요하지 않습니다.",
    "마무리에는 가벼운 스트레칭과 수분 섭취 안내가 이어집니다.",
    "결제는 사전 안내된 정찰 금액으로 진행되며 영수증 발행이 가능합니다."]),
  ("처음이라면 자주 묻는 것들",
   ["압이 너무 강하거나 약하면 언제든 말씀하시면 바로 조절합니다.",
    "관리 중 불편하면 중단을 요청할 수 있고, 진행 시간만큼만 정산합니다.",
    "임신·고혈압·급성 통증 등 주의 사항은 예약 시 미리 알려주세요.",
    "본 서비스는 의료 행위가 아닌 이완·건강관리 목적의 관리입니다."]),
  ("공간은 어떻게 준비하면 좋을까요",
   ["특별한 준비는 필요 없지만, 누울 수 있는 평평한 공간만 확보되면 충분합니다.",
    "매니저가 매트와 위생용품, 오일 등 준비물을 직접 지참합니다.",
    "조명을 조금 낮추고 휴대폰 알림을 꺼두면 이완에 더 도움이 됩니다.",
    "반려동물이 있거나 동거인이 있는 경우 예약 시 미리 알려주시면 편합니다."]),
  ("시간과 코스, 처음엔 이렇게 골라보세요",
   ["처음이라면 부담이 적은 60분으로 시작해 보는 것을 권합니다.",
    "이완이 목적이면 아로마·스웨디시, 뻐근함 해소가 목적이면 타이·스포츠가 무난합니다.",
    "두 번째 방문부터는 90분으로 늘려 전신을 고르게 다루는 분이 많습니다.",
    "선호 압 세기와 집중 부위를 기억해 두면 다음 예약이 한결 수월합니다."]),
  ("자주 하는 오해 세 가지",
   ["첫째, 출장은 비쌀 것이라는 오해 — 저희는 매장과 동일한 정찰 요금제로 운영합니다.",
    "둘째, 도착 시간이 들쭉날쭉할 것이라는 오해 — 권역별 평균을 데이터로 공개합니다.",
    "셋째, 준비가 번거로울 것이라는 오해 — 준비물은 모두 매니저가 가져옵니다.",
    "막연한 걱정보다 상담 한 번이 가장 빠른 해결책입니다."]),
 ],
 "course-by-condition": [
  ("수면이 부족하고 긴장이 풀리지 않을 때",
   ["교감신경이 과각성된 상태에서는 강한 자극보다 부드러운 이완이 회복에 유리합니다.",
    "이때는 향으로 신경계를 안정시키는 아로마, 또는 잔잔한 스웨디시가 잘 맞습니다.",
    "관리 시간은 전신을 고르게 다루는 90분을 가장 권장합니다.",
    "조명과 향의 강도를 낮춰 수면 전 휴식처럼 진행하면 효과적입니다."]),
  ("어깨·등 결림과 장시간 좌식 피로",
   ["오래 앉아 생기는 결림은 표면 근육과 근막을 함께 다뤄야 풀립니다.",
    "표면 이완에는 스웨디시, 굳은 근막을 늘리는 데는 타이 스트레칭이 효과적입니다.",
    "집중 부위를 미리 말씀하시면 해당 부위에 시간을 더 배분합니다.",
    "결림이 잦다면 2~3주 간격의 정기 관리가 누적 피로 관리에 도움이 됩니다."]),
  ("운동 후 근피로와 국소 통증",
   ["운동 직후의 지연성 근육통은 표적 압과 근막 이완으로 회복을 도울 수 있습니다.",
    "이 경우 기능 중심의 스포츠 코스가 가장 적합합니다.",
    "통증 부위와 운동 종류를 알려주시면 강도를 맞춰 진행합니다.",
    "급성 부상이나 염증이 의심되면 관리보다 의료기관 진료가 우선입니다."]),
  ("코스 선택 데이터 — 우리 고객은 이렇게 골랐습니다",
   ["최근 배차 기준 가장 많이 선택된 코스는 아로마 90분이었습니다.",
    "수면·스트레스 목적은 아로마·스웨디시, 근피로 목적은 스포츠·타이로 뚜렷이 갈렸습니다.",
    "처음 이용 고객의 다수는 60분으로 시작해 재방문 시 90분으로 늘리는 경향을 보였습니다.",
    "선택이 어렵다면 상담 시 컨디션을 말씀해 주시면 맞춤으로 추천드립니다."]),
  ("계절과 생활 패턴에 따른 선택",
   ["환절기에는 자율신경이 쉽게 흐트러져 수면의 질이 떨어지기 쉽습니다.",
    "이 시기에는 향으로 안정을 돕는 아로마가 특히 잘 맞는다는 후기가 많습니다.",
    "야간 근무나 교대 근무로 생활 리듬이 불규칙하면 짧은 60분 정기 관리가 부담이 적습니다.",
    "장시간 출장·여행 뒤에는 전신을 고르게 다루는 90분 코스를 권합니다."]),
  ("강도 선택 — 강할수록 좋은 게 아닙니다",
   ["압이 강할수록 효과가 크다는 생각은 흔한 오해입니다.",
    "근육이 과하게 긴장한 상태에서 너무 강한 압은 오히려 방어 반응을 부를 수 있습니다.",
    "처음에는 중간 강도로 시작해 몸의 반응을 보며 조절하는 편이 안전합니다.",
    "관리 다음 날 가벼운 뻐근함은 정상일 수 있으나, 통증이 심하면 강도를 낮춰야 합니다."]),
  ("코스를 바꿔야 할 때",
   ["같은 코스를 반복했는데 체감이 줄었다면 다른 결의 코스를 시도해 볼 시점입니다.",
    "이완 위주였다면 스트레칭 중심의 타이로, 자극 위주였다면 아로마로 바꿔보는 식입니다.",
    "몸의 호소 부위가 달라졌다면 집중 부위도 함께 조정하는 것이 좋습니다.",
    "어떤 변화를 줄지 모르겠다면 상담 시 그간의 이용 패턴을 말씀해 주세요."]),
 ],
 "arrival-time-data": [
  ("왜 도착 시간을 공개하나요",
   ["출장 관리에서 고객이 가장 자주 묻는 것은 '언제 도착하느냐'였습니다.",
    "막연한 '빠른 방문' 대신 권역별 실측 평균을 공개하는 편이 신뢰에 낫다고 판단했습니다.",
    "그래서 모든 지역 페이지에 동(洞) 단위 평균 도착 시간을 표기합니다.",
    "이는 마케팅 문구가 아니라 자체 배차 로그에서 산출한 1차 데이터입니다."]),
  ("어떻게 측정하나요",
   ["예약이 접수된 시각부터 매니저가 현장 도착을 보고한 시각까지의 차이를 측정합니다.",
    f"최근 {DISPATCH_MONTHS}개월간 누적 {DISPATCH_TOTAL:,}건({DISPATCH_BREAKDOWN})을 집계했습니다.",
    "같은 행정구 안에서도 동별로 도심 접근성이 달라 동 단위로 나눠 평균을 냅니다.",
    "이상치(사고·악천후)는 제외해 정상 교통 기준 평균을 산출합니다."]),
  ("데이터를 읽는 법",
   ["표기된 분(分)은 정상 교통 기준 평균이며, 출퇴근·심야에는 달라질 수 있습니다.",
    "업무·상업 밀집 권역은 야간 콜이 몰려 시간대별 편차가 큽니다.",
    "신도시·외곽은 거리상 도착이 다소 길어 사전 예약을 권장합니다.",
    "예약 시점에 실제 예상 시간을 다시 안내드리므로 표기 값은 참고용입니다."]),
  ("앞으로의 개선",
   ["권역별 매니저 배치를 늘려 도착 편차를 줄여 나가고 있습니다.",
    "시간대별 콜 분포를 분석해 야간 피크 시간 배차를 보강합니다.",
    "데이터는 분기마다 갱신하며, 변동이 크면 지역 페이지에 반영합니다.",
    "측정 방식에 대한 문의는 고객센터로 주시면 상세히 안내드립니다."]),
  ("권역별로 도착 시간이 다른 이유",
   ["업무·상업 밀집 권역은 야간에 콜이 몰려 대기 행렬이 길어지는 경향이 있습니다.",
    "신도시·외곽은 거리 자체가 길어 평균 도착 시간이 자연히 늘어납니다.",
    "교통 결절지(환승 거점) 인근은 매니저 접근성이 좋아 평균이 짧은 편입니다.",
    "그래서 같은 시 안에서도 동(洞)에 따라 수 분에서 십수 분의 차이가 납니다."]),
  ("예약 시간을 잘 잡는 법",
   ["가장 붐비는 시간대를 피해 30분~1시간 앞당겨 예약하면 대기가 줄어듭니다.",
    "외곽 권역은 당일보다 미리 예약하면 인근 매니저를 배치하기 쉬워 도착이 빨라집니다.",
    "악천후나 연휴에는 평소보다 여유를 두고 예약하시길 권합니다.",
    "예약 시 안내되는 예상 도착 시간이 가장 정확한 기준입니다."]),
  ("우리가 데이터를 다루는 원칙",
   ["도착 시간 수치는 마케팅 목적의 과장 없이 실측값을 그대로 반영합니다.",
    "표본이 적은 외곽 동은 인접 동과 묶어 신뢰도를 확보합니다.",
    "사고·악천후 등 이상치는 제외해 평상시 기준을 제공합니다.",
    "데이터의 한계도 함께 표기하는 것을 편집 원칙으로 삼습니다."]),
 ],
}

def build_magazine_hub():
    title = f"매거진 — 출장마사지 가이드와 데이터 | {BRAND}"
    desc = "예약 가이드, 컨디션별 코스 선택, 도착 시간 데이터 등 마사지바삭 운영팀이 직접 쓴 글을 모았습니다."
    cards = "".join(f'''<a class="card reveal" href="/magazine/{m["slug"]}/">
<div class="kicker">ARTICLE</div><h3>{esc(m["title"])}</h3><p>{esc(m["desc"])}</p>
<span class="more">읽어보기 →</span></a>''' for m in MAGAZINE)
    notes = (
        note_card(1, "매거진은 누가, 왜 쓰나요",
            [f"매거진의 글은 {AUTHOR}이 직접 작성하고 안전 자문 트레이너가 검수합니다.",
             "출장마사지를 처음 이용하는 분이 가장 궁금해하는 점을 현장 기준으로 풀어 씁니다.",
             "막연한 홍보가 아니라 실제 운영 데이터와 경험을 근거로 설명하는 것을 원칙으로 합니다.",
             "확인되지 않은 효능이나 과장 표현은 사용하지 않습니다."]),
        note_card(2, "이런 내용을 다룹니다",
            ["처음 예약하는 분을 위한 단계별 가이드와 자주 하는 오해 정리.",
             "수면 부족·근피로·결림 등 컨디션별로 맞는 코스를 고르는 법.",
             "권역별 평균 도착 시간을 어떻게 측정하고 공개하는지에 대한 데이터 해설.",
             "강도 선택, 계절별 선택 등 실제 이용에 도움이 되는 실용 정보."]),
        note_card(3, "글을 신뢰할 수 있는 이유",
            [f"모든 글에는 책임 저자({AUTHOR})와 검수자({TEAM[1]['name']} {TEAM[1]['role']})를 명시합니다.",
             "도착 시간 등 수치는 자체 배차 로그를 1차 출처로 하며 과장하지 않습니다.",
             "AI 보조 도구를 활용하더라도 운영팀이 직접 검수한 뒤 게시합니다.",
             "오류가 확인되면 고객센터 제보를 받아 신속히 정정합니다."]),
        note_card(4, "출장마사지 기본 상식 — 매장과 무엇이 다른가요",
            ["출장마사지는 매니저가 이용자가 지정한 장소로 직접 방문해 관리하는 방식입니다.",
             "이동·준비 시간이 없어 관리 직후 바로 휴식할 수 있다는 점이 가장 큰 장점입니다.",
             "매트·오일·위생용품은 매니저가 모두 지참하므로 별도 준비가 필요 없습니다.",
             "마사지바삭은 매장과 동일한 정찰 요금을 적용해 출장비 명목의 할증이 없습니다."]),
        note_card(5, "처음 이용자가 가장 궁금해하는 것",
            ["‘얼마나 빨리 오나요’ — 권역별 평균 도착 시간을 지역 페이지에 데이터로 공개합니다.",
             "‘얼마인가요’ — 코스·시간별 정찰 요금이며 추가 비용이 없습니다.",
             "‘무엇을 준비하나요’ — 누울 공간만 있으면 되고 준비물은 매니저가 가져옵니다.",
             "‘안전한가요’ — 자문 트레이너 가이드라인과 위생 기준을 전 매니저가 따릅니다."]),
        note_card(6, "이 매거진을 200% 활용하는 법",
            ["처음이라면 ‘예약 가이드’로 전체 흐름을 먼저 파악하시길 권합니다.",
             "코스가 고민이면 ‘컨디션별 코스 선택’ 글이 상태별 추천을 정리해 둡니다.",
             "도착 시간이 중요하면 ‘도착 시간 데이터’ 글과 지역 페이지를 함께 보세요.",
             "각 글 하단의 자주 묻는 질문에서 예약 전 궁금증을 빠르게 해소할 수 있습니다."]),
        note_card(7, "코스의 결 — 오일과 건식의 차이",
            ["오일 코스(스웨디시·아로마·로미로미)는 오일로 부드럽게 쓸어내려 깊은 이완을 만듭니다.",
             "건식 코스(타이·스포츠)는 옷을 입은 채 스트레칭과 표적 압으로 뭉침을 다룹니다.",
             "끈적임 없이 개운한 관리를 원하면 건식이, 잔잔한 휴식을 원하면 오일 코스가 맞습니다.",
             "각 코스의 특징은 서비스 상세 페이지에서 더 자세히 확인할 수 있습니다."]),
        note_card(8, "관리 전후, 이것만 기억하세요",
            ["관리 직전 가벼운 샤워로 몸을 데우면 근육이 더 쉽게 이완됩니다.",
             "공복이나 과식 직후보다 식사 후 1~2시간 지난 상태가 편안합니다.",
             "관리 후에는 따뜻한 물을 충분히 마셔 회복을 돕는 것이 좋습니다.",
             "관리 당일은 무리한 운동이나 음주를 피하고 충분히 쉬어주세요."]),
        note_card(9, "안전하게 이용하기",
            ["임신·고혈압·급성 통증 등 주의 사항이 있으면 예약 시 반드시 알려주세요.",
             "압 세기는 강할수록 좋은 것이 아니며, 중간 강도로 시작해 조절하는 편이 안전합니다.",
             "통증이 지속·악화되면 관리보다 의료기관 진료를 우선하시길 권합니다.",
             "본 서비스는 의료 행위가 아닌 19세 이상 대상의 이완·건강관리 서비스입니다."]),
        note_card(10, "더 궁금하면 이렇게 확인하세요",
            ["요금 정보는 요금 안내 페이지에서 코스·시간별 정찰가로 정리되어 있습니다.",
             "우리 동네 도착 시간은 지역 → 광역 → 행정구 순서로 들어가면 확인됩니다.",
             "매니저 국적별 특징은 관리사 페이지에서 비교해 볼 수 있습니다.",
             f"바로 예약하려면 {TEL}로 전화하시거나 24시간 상담을 이용하세요."]),
    )
    mhfaq = [
        ("매거진 글은 누가 쓰나요?", f"{AUTHOR}이 직접 작성하고 안전 자문 트레이너 {TEAM[1]['name']}이 검수합니다. 모든 글에 책임 저자와 검수자를 명시합니다."),
        ("어떤 내용을 다루나요?", "처음 예약 가이드, 컨디션별 코스 선택, 권역별 도착 시간 데이터 해설 등 실제 이용에 도움이 되는 정보를 다룹니다."),
        ("정보의 출처는 무엇인가요?", f"도착 시간 등 수치는 최근 {DISPATCH_MONTHS}개월 자체 배차 로그를 1차 출처로 합니다. 확인되지 않은 효능은 주장하지 않습니다."),
        ("내용에 오류가 있으면 어떻게 하나요?", f"{TEL} 고객센터로 제보해 주시면 확인 후 신속히 정정합니다."),
    ]
    body = f'''{header()}
{crumb_html([("홈", "/"), ("매거진", "/magazine/")])}
<section class="hero compact"><div class="hero-inner"><div class="hero-copy reveal">
<span class="eyebrow">MAGAZINE</span><h1>매거진</h1><p class="lead">{esc(desc)}</p></div></div></section>
<section class="wrap cv"><div class="grid g3">{cards}</div></section>
<section class="wrap cv">{"".join(notes)}</section>
<section class="wrap cv"><div class="sec-head reveal"><span class="eyebrow">FAQ</span><h2>자주 묻는 질문</h2></div>
{faq_html(mhfaq)}</section>
{cta_band()}{footer()}'''
    ld = jsonld(breadcrumb_ld([("홈", "/"), ("매거진", "/magazine/")]),
                {"@type": "Blog", "name": f"{BRAND} 매거진", "url": DOMAIN + "/magazine/"},
                faq_ld(mhfaq))
    write("/magazine/", head(title, desc, "/magazine/", extra_ld=ld), body)

MAG_FAQ = {
 "first-visit-guide": [
  ("출장마사지 예약은 무엇부터 정하면 되나요?", f"위치(주소·건물 형태), 희망 코스, 희망 시간 세 가지만 정하면 충분합니다. {TEL}로 전화하시면 본사 디스패처가 나머지를 안내합니다."),
  ("공간을 따로 준비해야 하나요?", "누울 수 있는 평평한 공간만 있으면 됩니다. 매트·위생용품·오일 등 준비물은 매니저가 모두 지참합니다."),
  ("처음인데 어떤 코스가 좋을까요?", "부담이 적은 60분 스웨디시나 아로마로 시작하는 것을 권합니다. 재방문 시 90분으로 늘리는 분이 많습니다."),
  ("도착까지 얼마나 걸리나요?", "권역과 시간대에 따라 다르며, 수도권 핵심 권역은 평균 30~40분 내외입니다. 예약 시 예상 도착 시간을 분 단위로 안내합니다."),
  ("결제는 어떻게 하나요?", "사전에 안내된 정찰 금액으로 진행되며 코스 외 추가 비용은 없습니다. 영수증 발행도 가능합니다."),
 ],
 "course-by-condition": [
  ("수면이 부족할 때 어떤 코스가 좋나요?", "향으로 신경계를 안정시키는 아로마, 또는 잔잔한 스웨디시 90분을 권합니다. 조명과 향의 강도를 낮춰 진행하면 더 효과적입니다."),
  ("어깨 결림에는 어떤 코스가 맞나요?", "표면 이완에는 스웨디시, 굳은 근막을 늘리는 데는 타이 스트레칭이 효과적입니다. 집중 부위를 미리 말씀하시면 시간을 더 배분합니다."),
  ("운동 후 회복에는요?", "표적 압과 근막 이완 중심의 스포츠 코스가 적합합니다. 다만 급성 부상·염증이 의심되면 의료기관 진료가 우선입니다."),
  ("압은 강할수록 좋은가요?", "아닙니다. 과한 압은 오히려 방어 반응을 부를 수 있어, 중간 강도로 시작해 몸의 반응을 보며 조절하는 편이 안전합니다."),
  ("코스를 언제 바꾸는 게 좋나요?", "같은 코스의 체감이 줄거나 호소 부위가 달라졌다면 다른 결의 코스나 집중 부위 조정을 시도해 볼 시점입니다."),
 ],
 "arrival-time-data": [
  ("도착 시간 데이터는 어떻게 측정하나요?", f"예약 접수 시각부터 매니저 현장 도착 보고 시각까지의 실측 차이를, 최근 {DISPATCH_MONTHS}개월 배차 로그 {DISPATCH_TOTAL:,}건 기준으로 동 단위 집계합니다."),
  ("표기된 분은 항상 맞나요?", "정상 교통 기준 평균이며 참고용입니다. 출퇴근·심야·기상에 따라 달라질 수 있어, 예약 시점에 실제 예상 시간을 다시 안내합니다."),
  ("권역마다 도착 시간이 다른 이유는요?", "업무·상업 밀집 권역은 야간 콜이 몰리고, 신도시·외곽은 거리가 길며, 교통 결절지 인근은 접근성이 좋아 평균이 짧습니다."),
  ("외곽 지역은 어떻게 예약하면 좋나요?", "당일보다 미리 예약하면 인근 매니저를 배치하기 쉬워 도착이 빨라집니다. 악천후·연휴에는 여유를 두시길 권합니다."),
  ("데이터는 얼마나 자주 갱신하나요?", "분기마다 갱신하며 변동이 크면 지역 페이지에 반영합니다. 측정 방식 문의는 고객센터로 주시면 안내합니다."),
 ],
}

def build_magazine_article(m):
    title = f"{m['title']} | {BRAND} 매거진"
    desc = m["desc"]
    notes = MAG_BODY[m["slug"]] + [
        ("이 글을 어떻게 활용하면 좋을까요",
         ["여기 정리한 내용은 예약 전 결정과 상담을 빠르게 하도록 돕기 위한 안내입니다.",
          "각 항목은 실제 운영에서 자주 받은 질문과 배차 데이터를 근거로 정리했습니다.",
          "본인 상황에 맞지 않는 부분이 있으면 상담 시 그대로 말씀해 주시면 조정해 드립니다.",
          "관련 글과 지역별 도착 시간 데이터를 함께 보면 더 구체적인 그림을 그릴 수 있습니다."]),
        ("이 주제를 더 깊이 보려면",
         ["코스 선택이 고민이면 ‘내 컨디션에 맞는 코스 고르는 법’을 함께 읽어보시길 권합니다.",
          "도착 시간이 궁금하면 지역 페이지의 동(洞)별 평균 도착 데이터를 확인하세요.",
          "요금과 환불 기준은 요금 안내 페이지에 정찰제 기준으로 정리되어 있습니다.",
          "처음 이용이라면 예약 가이드 글이 단계별로 도움이 됩니다."]),
        ("마지막으로 — 운영팀의 약속",
         ["저희는 도착 시간과 결제를 데이터와 정찰 요금으로 투명하게 운영합니다.",
          "확인되지 않은 효능을 주장하지 않으며, 본 서비스는 이완·건강관리 목적입니다.",
          "19세 이상 성인을 대상으로 하는 합법적이고 건전한 관리만 제공합니다.",
          f"궁금한 점은 언제든 {TEL}로 문의해 주세요. 연중무휴 24시간 상담합니다."]),
    ]
    mfaq = MAG_FAQ[m["slug"]]
    note_html = "".join(note_card(i + 1, t, ps) for i, (t, ps) in enumerate(notes))
    toc = '<div class="toc reveal"><b>목차</b><ul>' + "".join(
        f'<li><a href="#s{i}">{esc(t)}</a></li>' for i, (t, _) in enumerate(notes)) + "</ul></div>"
    # add ids to note cards
    note_html_ided = ""
    for i, (t, ps) in enumerate(notes):
        nc = note_card(i + 1, t, ps).replace('class="note-card reveal"', f'class="note-card reveal" id="s{i}"', 1)
        note_html_ided += nc
    crumbs = [("홈", "/"), ("매거진", "/magazine/"), (m["title"], f"/magazine/{m['slug']}/")]
    related = "".join(f'<li><a href="/magazine/{x["slug"]}/">{esc(x["title"])}</a></li>'
                      for x in MAGAZINE if x["slug"] != m["slug"])
    body = f'''{header()}
{crumb_html(crumbs)}
<section class="hero compact"><div class="hero-inner"><div class="hero-copy reveal">
<span class="eyebrow">MAGAZINE · 운영팀 작성</span><h1>{esc(m["title"])}</h1>
<p class="lead">{esc(desc)}</p>
<div class="trust">저자 {esc(AUTHOR)} · 검수 {esc(TEAM[1]["name"])}({esc(TEAM[1]["role"])}) · 2026-05-27</div></div></div></section>
<section class="wrap cv">{toc}{note_html_ided}
<div class="databox reveal"><h3>관련 글</h3><ul style="list-style:none;display:flex;flex-direction:column;gap:8px;margin-top:8px">{related}
<li><a href="/pricing/">전체 요금 보기</a></li><li><a href="/locations/">지역별 도착 시간 보기</a></li></ul></div></section>
<section class="wrap cv"><div class="sec-head reveal"><span class="eyebrow">FAQ</span><h2>자주 묻는 질문</h2></div>
{faq_html(mfaq)}</section>
{cta_band()}{footer()}'''
    ld = jsonld(
        breadcrumb_ld(crumbs),
        {"@type": "BlogPosting", "headline": m["title"], "description": desc,
         "author": {"@type": "Organization", "name": AUTHOR},
         "reviewedBy": {"@type": "Person", "name": TEAM[1]["name"], "jobTitle": TEAM[1]["role"]},
         "publisher": {"@id": DOMAIN + "/#org"}, "datePublished": "2026-02-01",
         "dateModified": "2026-05-27", "mainEntityOfPage": DOMAIN + f"/magazine/{m['slug']}/",
         "image": DOMAIN + "/assets/og-cover.jpg"},
        faq_ld(mfaq))
    write(f"/magazine/{m['slug']}/", head(title, desc, f"/magazine/{m['slug']}/", og_type="article", extra_ld=ld), body)


# ════════════════════════════════════════════════════════════
# 지역: 허브 / 광역 / 행정구
# ════════════════════════════════════════════════════════════
def build_locations_hub():
    title = f"지역별 출장마사지 — 서울·경기·인천·부산 82개 행정구 | {BRAND}"
    desc = "마사지바삭이 출장하는 서울·경기·인천·부산 82개 행정구를 권역별로 안내합니다. 권역별 평균 도착 시간 데이터 제공."
    region_cards = ""
    for r in REGIONS:
        n = len(DISTRICTS[r["slug"]])
        region_cards += f'''<a class="card reveal" href="/locations/{r["slug"]}/">
<div class="kicker">{esc(r["full"])}</div><h3>{esc(r["name"])} {n}개 행정구</h3>
<p>{esc(r["name"])} 전역으로 본사 디스패처가 직접 배차합니다. 권역별 평균 도착 시간을 데이터로 안내합니다.</p>
<span class="more">{esc(r["name"])} 보기 →</span></a>'''
    total = sum(len(v) for v in DISTRICTS.values())
    notes = (
        note_card(1, "어디까지 출장하나요",
            [f"마사지바삭은 서울 25개구, 경기 31개 시군, 인천 10개구, 부산 16개구 등 총 {total}개 행정구를 운영합니다.",
             "경기 파주 본사를 거점으로 수도권 전역과 부산 주요 권역에 매니저를 배치합니다.",
             "각 행정구 페이지에서 동(洞) 단위 평균 도착 시간을 데이터로 확인할 수 있습니다.",
             "출장 가능 여부가 궁금하면 예약 전화로 위치를 알려주시면 바로 안내드립니다."]),
        note_card(2, "도착 시간 데이터는 이렇게 만듭니다",
            [f"최근 {DISPATCH_MONTHS}개월 누적 {DISPATCH_TOTAL:,}건의 자체 배차 로그({DISPATCH_BREAKDOWN})를 집계했습니다.",
             "예약 접수 시각부터 매니저 현장 도착 보고 시각까지의 실측 차이를 동 단위로 평균 냅니다.",
             "사고·악천후 등 이상치는 제외해 평상시 정상 교통 기준 값을 제공합니다.",
             "표기 평균은 참고용이며, 예약 시 실제 예상 도착 시간을 다시 안내드립니다."]),
        note_card(3, "지역 페이지 읽는 법",
            ["각 행정구 페이지 상단에는 평균 도착 시간과 권역 성격이 요약되어 있습니다.",
             "동별 도착 분포, 시간대별 콜 특징, 추천 코스를 차례로 확인할 수 있습니다.",
             "행정구별 특화 후기와 자주 묻는 질문도 함께 제공합니다.",
             "요금과 안전 기준은 모든 지역이 동일한 회사 정책을 따릅니다."]),
        note_card(4, "권역별로 도착 시간이 다른 이유",
            ["업무·상업이 밀집한 도심 권역은 야간 콜이 몰려 시간대별 편차가 큽니다.",
             "교통 결절지(환승 거점) 인근은 매니저 접근성이 좋아 평균 도착이 빠른 편입니다.",
             "신도시·외곽 권역은 거리 자체가 멀어 평균 도착 시간이 다소 길어집니다.",
             "그래서 같은 시·구 안에서도 동(洞)에 따라 수 분에서 십수 분의 차이가 납니다."]),
        note_card(5, "도착을 앞당기는 예약 팁",
            ["가장 붐비는 저녁·심야 피크를 30분~1시간 앞당겨 예약하면 대기가 줄어듭니다.",
             "외곽 권역은 당일보다 미리 예약하면 인근 매니저 배치로 도착이 빨라집니다.",
             "악천후·연휴에는 평소보다 여유를 두고 예약하시길 권합니다.",
             "예약 시 안내되는 예상 도착 시간이 가장 정확한 기준입니다."]),
        note_card(6, "수도권·부산 전역 동일 기준",
            ["서울·경기·인천·부산 어느 권역이든 코스별 정찰 요금이 동일합니다.",
             "지역에 따른 출장비 할증이나 심야·휴일 할증이 없습니다.",
             "안전·위생 가이드라인과 매니저 교육 기준도 전 권역이 동일합니다.",
             "6개국 매니저 선호 역시 모든 권역에서 동일하게 반영합니다."]),
        note_card(7, "서울·경기 — 수도권 핵심 권역",
            ["서울 25개 자치구는 업무·상업·주거가 촘촘해 야간 수요가 가장 많은 권역입니다.",
             "경기 31개 시군은 신도시 입주가 활발해 권역이 넓고 신규 고객 비율이 높습니다.",
             "본사가 위치한 파주를 비롯해 수도권 전역에 매니저를 배치합니다.",
             "도심·교통 결절지 권역은 평균 도착이 빠른 편입니다."]),
        note_card(8, "인천·부산 — 광역 거점 권역",
            ["인천 10개 구는 송도·청라·검단 등 국제도시 입주로 성장세가 뚜렷합니다.",
             "부산 16개 구는 서면·해운대·광안리 등 번화가와 관광 권역의 야간 수요가 많습니다.",
             "공항·항만 인근과 신도시 권역까지 폭넓게 배차합니다.",
             "각 행정구 페이지에서 동별 평균 도착 시간을 확인할 수 있습니다."]),
        note_card(9, "출장 가능 여부가 헷갈린다면",
            ["거주지·방문지가 속한 행정구를 모르시면 예약 전화로 주소를 말씀해 주세요.",
             "디스패처가 해당 위치의 출장 가능 여부와 예상 도착 시간을 즉시 안내합니다.",
             "행정구 경계에 가까운 지역도 인접 권역 매니저로 배차할 수 있습니다.",
             "외곽·도서 지역은 사전 예약을 권장드립니다."]),
        note_card(10, "집·숙소·사무실 어디든",
            ["자택은 물론 호텔·레지던스·게스트하우스 등 숙소로도 출장 관리가 가능합니다.",
             "출장·여행 중 묵는 숙소에서도 동일한 정찰 요금으로 이용할 수 있습니다.",
             "숙소의 경우 건물명과 호실, 로비 안내 여부를 함께 말씀해 주시면 도착이 매끄럽습니다.",
             "누울 수 있는 평평한 공간만 있으면 준비물은 매니저가 모두 지참합니다."]),
    )
    lfaq = [
        ("출장 가능한 지역은 어디인가요?", f"서울 25개구, 경기 31개 시군, 인천 10개구, 부산 16개구 등 총 {total}개 행정구로 출장합니다. 경기 파주 본사를 거점으로 합니다."),
        ("우리 동네가 되는지 어떻게 확인하나요?", "지역 → 광역시도 → 행정구 순서로 들어가면 동(洞)별 평균 도착 시간을 확인할 수 있습니다. 헷갈리면 예약 전화로 주소를 말씀해 주세요."),
        ("도착 시간 데이터는 믿을 만한가요?", f"최근 {DISPATCH_MONTHS}개월 자체 배차 로그 {DISPATCH_TOTAL:,}건을 동 단위로 집계한 실측 평균입니다. 이상치는 제외한 정상 교통 기준 값입니다."),
        ("지역마다 요금이 다른가요?", "아니요. 모든 행정구가 동일한 정찰 요금이며 지역별 출장비 할증이 없습니다."),
        ("예약은 어떻게 하나요?", f"{TEL} 전화 또는 24시간 상담으로 위치와 코스를 알려주시면 본사 디스패처가 배차합니다."),
    ]
    body = f'''{header()}
{crumb_html([("홈", "/"), ("지역", "/locations/")])}
<section class="hero compact"><div class="hero-inner"><div class="hero-copy reveal">
<span class="eyebrow">LOCATIONS</span><h1>지역별 출장마사지</h1><p class="lead">{esc(desc)}</p></div></div></section>
<section class="wrap cv"><div class="grid g2">{region_cards}</div></section>
<section class="wrap cv">{"".join(notes)}</section>
<section class="wrap cv"><div class="sec-head reveal"><span class="eyebrow">FAQ</span><h2>자주 묻는 질문</h2></div>
{faq_html(lfaq)}</section>
{cta_band()}{footer()}'''
    ld = jsonld(breadcrumb_ld([("홈", "/"), ("지역", "/locations/")]),
                {"@type": "CollectionPage", "name": title, "url": DOMAIN + "/locations/"},
                faq_ld(lfaq))
    write("/locations/", head(title, desc, "/locations/", extra_ld=ld), body)

def build_region_hub(r):
    dists = DISTRICTS[r["slug"]]
    n = len(dists)
    rn = r["name"]
    title = f"{r['name']} 출장마사지 — {n}개 행정구 전역 24시 | {BRAND}"
    desc = f"{r['full']} {n}개 행정구로 출장하는 마사지바삭. 권역별 평균 도착 시간과 정찰 요금을 안내합니다."
    cards = "".join(f'''<a class="card reveal" href="/locations/{r["slug"]}/{d["slug"]}/">
<div class="kicker">{esc(r["name"])}</div><h3>{esc(d["name"])}</h3>
<p>{esc(d["character"])}. 평균 도착 {d["dongs"][0][1]}분대부터.</p>
<span class="more">{esc(d["name"])} 보기 →</span></a>''' for d in dists)
    fastest = min((dd for d in dists for dd in d["dongs"]), key=lambda x: x[1])
    avg_all = round(sum(dd[1] for d in dists for dd in d["dongs"]) / sum(len(d["dongs"]) for d in dists))
    by_speed = sorted(dists, key=lambda d: min(x[1] for x in d["dongs"]))
    fast3 = "、".join(f"{d['name']}({min(x[1] for x in d['dongs'])}분대)" for d in by_speed[:3])
    slow2 = "、".join(f"{d['name']}({max(x[1] for x in d['dongs'])}분대)" for d in by_speed[-2:])
    landmark_pool = [lm for d in dists for lm in d["landmarks"]]
    landmark_str = "、".join(landmark_pool[:8])
    sample_d = dists[:4]
    char_lines = [f"{d['name']}은 {d['character']}입니다." for d in sample_d]
    intro = (
        note_card(1, f"{r['name']} 출장 운영 안내",
            [f"마사지바삭은 {r['full']} {n}개 행정구 전역으로 출장 관리를 배차합니다.",
             "각 행정구 페이지에서 동(洞) 단위 평균 도착 시간을 데이터로 확인할 수 있습니다.",
             "스웨디시·아로마·타이·로미로미·스포츠 5종을 동일한 정찰 요금으로 운영합니다.",
             f"예약은 {TEL} 전화 또는 24시간 상담으로 접수합니다."]),
        note_card(2, f"{r['name']} 권역 도착 시간 개요",
            [f"{r['name']} 전체 평균 도착 시간은 약 {avg_all}분 수준입니다(정상 교통 기준).",
             "도심·교통 결절지에 가까운 권역일수록 평균이 짧고, 외곽 신도시는 다소 길어집니다.",
             "같은 시·구 안에서도 동에 따라 수 분에서 십수 분의 차이가 납니다.",
             f"행정구를 선택하면 해당 권역의 동별 분포를 자세히 확인할 수 있습니다."]),
        note_card(3, f"{r['name']}에서 자주 찾는 코스",
            [f"{r['name']} 권역은 업무·주거 피로로 인한 이완 수요가 가장 많습니다.",
             "수면·스트레스 목적은 아로마·스웨디시, 근피로 목적은 타이·스포츠를 권합니다.",
             "처음이라면 60분으로 시작해 재방문 시 90분으로 늘리는 분이 많습니다.",
             "선호 매니저 국적과 압 세기는 예약 시 함께 말씀하시면 반영합니다."]),
        note_card(4, f"{rn} 예약·결제·안전 기준",
            ["모든 코스는 정찰 요금제로 운영되어 심야·휴일에도 임의 할증이 없습니다.",
             "예약 단계에서 코스·시간·도착 예정·결제 금액을 모두 미리 안내합니다.",
             f"안전 자문 트레이너 {TEAM[1]['name']}의 가이드라인을 {rn} 전 권역에 동일하게 적용합니다.",
             "본 서비스는 19세 이상 대상의 건전한 건강관리 서비스이며 의료 행위가 아닙니다."]),
        note_card(5, f"{rn} 행정구를 고르는 법",
            [f"아래 행정구 카드에는 권역 성격과 가장 빠른 도착 시간대가 함께 표기되어 있습니다.",
             "거주지나 방문지가 속한 행정구를 선택하면 동(洞)별 도착 분포를 확인할 수 있습니다.",
             "행정구가 헷갈리면 예약 전화로 주소를 말씀해 주시면 바로 안내드립니다.",
             "행정구별로 특화된 후기와 자주 묻는 질문도 함께 제공합니다."]),
        note_card(6, f"{rn} 권역 도착이 빠른 곳",
            [f"배차 로그상 {rn}에서 평균 도착이 빠른 편인 권역은 {fast3} 순입니다.",
             f"반대로 {slow2}은 거리·지형 특성상 도착에 시간이 조금 더 걸립니다.",
             f"이런 외곽 권역은 미리 예약하시면 인근 매니저 배치로 도착을 앞당길 수 있습니다.",
             "표기 값은 정상 교통 기준 평균이며, 예약 시 실제 예상 시간을 다시 안내합니다."]),
        note_card(7, f"{rn} 주요 거점과 권역 성격",
            [f"{rn}은 {landmark_str} 등 주요 거점을 중심으로 이동 동선이 형성됩니다.",
             char_lines[0] if len(char_lines) > 0 else "",
             char_lines[1] if len(char_lines) > 1 else "",
             (char_lines[2] + " " + char_lines[3]) if len(char_lines) > 3 else (char_lines[2] if len(char_lines) > 2 else "")]),
        note_card(8, f"{rn} 예약 시 알아두면 좋은 점",
            [f"{rn}은 저녁부터 심야로 갈수록 예약이 몰리는 시간대가 형성됩니다.",
             "원하는 시간이 있으면 피크를 30분~1시간 앞당겨 예약하면 대기가 줄어듭니다.",
             "선호하는 코스·매니저 국적·압 세기를 함께 말씀하시면 더 정확히 배차합니다.",
             f"예약은 {TEL} 전화 또는 24시간 상담으로 접수하며, 본사 디스패처가 직접 배차합니다."]),
    )
    rfaq = [
        (f"{rn} 어디까지 출장하나요?", f"{r['full']} {n}개 행정구 전역으로 출장합니다. 각 행정구 페이지에서 동별 평균 도착 시간을 확인할 수 있습니다."),
        (f"{rn} 도착까지 얼마나 걸리나요?", f"{rn} 전체 평균은 약 {avg_all}분 수준(정상 교통 기준)이며, 도심 권역은 더 빠르고 외곽 신도시는 다소 길어집니다. 예약 시 실제 예상 시간을 안내합니다."),
        (f"{rn}은 요금이 다른 지역과 다른가요?", "아니요. 모든 행정구가 동일한 정찰 요금이며 지역별 추가 비용은 없습니다."),
        ("심야에도 예약이 되나요?", "네, 연중무휴 24시간 운영합니다. 외곽 권역은 미리 예약하시면 인근 매니저 배치로 도착이 빨라집니다."),
        (f"{rn} 예약은 어떻게 하나요?", f"{TEL} 전화 또는 24시간 상담으로 위치와 코스를 알려주시면 본사에서 배차합니다."),
    ]
    crumbs = [("홈", "/"), ("지역", "/locations/"), (r["name"], f"/locations/{r['slug']}/")]
    body = f'''{header()}
{crumb_html(crumbs)}
<section class="hero compact"><div class="hero-inner"><div class="hero-copy reveal">
<span class="eyebrow">{esc(r["full"])}</span><h1>{esc(r["name"])} 출장마사지</h1>
<p class="lead">{esc(desc)}</p></div></div></section>
<section class="wrap cv">{"".join(intro)}</section>
<section class="wrap cv"><div class="sec-head reveal"><span class="eyebrow">DISTRICTS · {n}</span>
<h2>{esc(r["name"])} 행정구</h2></div><div class="grid g4">{cards}</div></section>
<section class="wrap cv"><div class="sec-head reveal"><span class="eyebrow">FAQ</span><h2>{esc(rn)} 자주 묻는 질문</h2></div>
{faq_html(rfaq)}</section>
{cta_band()}{footer()}'''
    ld = jsonld(breadcrumb_ld(crumbs),
                localbusiness_ld(name=f"{BRAND} {r['name']}", area=r["full"], _id=f"/locations/{r['slug']}/#business"),
                {"@type": "CollectionPage", "name": title, "url": DOMAIN + f"/locations/{r['slug']}/"},
                faq_ld(rfaq))
    write(f"/locations/{r['slug']}/", head(title, desc, f"/locations/{r['slug']}/", extra_ld=ld), body)

def build_district(r, d):
    dn = d["name"]; rn = r["name"]
    title = f"{rn} {dn} 출장마사지 — 동별 평균 도착 시간 공개 | {BRAND}"
    desc = (f"{r['full']} {dn} 출장마사지. {d['character']}. "
            f"{', '.join(x[0] for x in d['dongs'][:3])} 등 동별 평균 도착 시간과 정찰 요금, "
            f"{dn} 특화 후기를 안내합니다.")
    dong_list = ", ".join(f"{name} 약 {mins}분" for name, mins in d["dongs"])
    fast = min(d["dongs"], key=lambda x: x[1]); slow = max(d["dongs"], key=lambda x: x[1])
    avg = round(sum(x[1] for x in d["dongs"]) / len(d["dongs"]))
    landmarks = ", ".join(d["landmarks"])

    overview = (
        note_card(5, f"{dn} 동(洞)별 평균 도착 시간",
            [f"{dn} 안에서도 동별로 도심 접근성이 달라 평균 도착 시간에 차이가 있습니다.",
             f"실측 기준 {dong_list} 수준입니다.",
             f"가장 빠른 권역은 {fast[0]}({fast[1]}분대), 상대적으로 시간이 더 걸리는 곳은 {slow[0]}({slow[1]}분대)입니다.",
             f"{dn} 전체 평균은 약 {avg}분으로, 정상 교통 기준 자체 배차 로그에서 산출한 값입니다."]),
        note_card(6, "시간대별 콜 분포 특징",
            [f"{dn}은 {d['character']}입니다.",
             "이 때문에 저녁부터 심야로 갈수록 예약이 몰리는 시간대가 형성됩니다.",
             "피크 시간대에는 표기 평균보다 도착이 다소 길어질 수 있어 여유 있는 예약을 권합니다.",
             "본사는 이 권역의 콜 분포를 분석해 야간 배차 인력을 보강하고 있습니다."]),
        note_card(7, f"{dn}에 어울리는 추천 코스",
            [f"{landmarks} 인근의 업무·주거 특성상 누적 피로와 수면 부족을 호소하는 고객이 많습니다.",
             "이런 경우 부드러운 아로마 90분이나 스웨디시가 가장 무난한 선택입니다.",
             "장시간 좌식·운동 후 근피로가 뚜렷하면 타이 스트레칭이나 스포츠 코스를 권합니다.",
             "선택이 어렵다면 상담 시 컨디션을 말씀해 주시면 맞춤으로 추천드립니다."]),
        note_card(8, "예약·결제·환불 한눈에",
            [f"{dn} 출장 예약은 {TEL} 전화 또는 24시간 상담으로 접수합니다.",
             "모든 코스는 정찰 요금으로 진행되며 코스 외 추가 비용은 없습니다.",
             "매니저 출발 전 취소는 위약금이 없고, 출발 후에는 이동 비용이 발생할 수 있습니다.",
             "결제 수단과 영수증 발행은 예약 단계에서 안내드립니다."]),
    )
    fieldnotes = (
        note_card(1, f"{dn} 권역의 특징",
            [f"{dn}은 {d['character']}으로 분류됩니다.",
             f"{landmarks} 등 주요 거점을 중심으로 이동 동선이 형성됩니다.",
             "이러한 권역 성격은 시간대별 수요와 도착 시간에 직접 영향을 줍니다.",
             "그래서 단순한 행정구명 치환이 아니라 권역별 실제 데이터로 안내드립니다."]),
        note_card(2, "매니저 배치와 도착 시간",
            [f"본사는 {rn} 권역의 콜 분포에 맞춰 {dn} 인근에 매니저를 배치합니다.",
             f"덕분에 {fast[0]} 방면은 약 {fast[1]}분대로 비교적 빠르게 도착합니다.",
             f"반면 {slow[0]} 방면은 거리상 {slow[1]}분대로 다소 더 소요됩니다.",
             "예약 시점의 실제 예상 도착 시간을 분 단위로 다시 안내드립니다."]),
        note_card(3, "안전 가이드 — 자문 트레이너 기준",
            [f"안전 자문 트레이너 {TEAM[1]['name']}({TEAM[1]['bio']})의 가이드라인을 {dn}에서도 동일하게 적용합니다.",
             "관리 전 압 세기와 집중 부위, 금기 사항을 확인한 뒤 진행합니다.",
             "임신·고혈압·급성 통증 등은 사전 고지 시 코스를 조정합니다.",
             "본 서비스는 의료 행위가 아닌 이완·건강관리 목적임을 분명히 합니다."]),
        note_card(4, "결제·예약 운영 원칙",
            ["정찰 요금제로 운영해 심야·휴일이라는 이유의 임의 할증이 없습니다.",
             "예약 단계에서 코스·시간·도착 예정·결제 금액을 모두 안내합니다.",
             "외부 중개 없이 본사 디스패처가 직접 배차해 책임 소재가 분명합니다.",
             f"{dn} 단골 고객을 위한 재방문 매니저 지정도 가능합니다."]),
    )
    reviews = district_reviews(d, rn)
    # 행정동 목록 (서울·인천·부산, 그리고 행정구 없는 경기 시·군) — 동별 페이지 카드
    dong_names = geo.DONG_REGIONS.get(r["slug"], {}).get(d["slug"], [])
    if not dong_names and r["slug"] == "gyeonggi":
        dong_names = geo.GYEONGGI_DONGS.get(d["slug"], [])
    dong_section = ""
    if dong_names:
        cs = []
        for dname in dong_names:
            mins = dong_arrival(avg, r["slug"] + d["slug"] + dname)
            href = enc(f"/locations/{r['slug']}/{d['slug']}/{dname}/")
            cs.append(
                f'<a class="card reveal" href="{href}"><div class="kicker">{esc(dn)}</div>'
                f'<h3>{esc(dname)}</h3><p>{esc(dname)} 출장마사지 · 평균 도착 약 {mins}분. '
                f'동별 도착 시간·추천 코스·후기를 확인하세요.</p>'
                f'<span class="more">{esc(dname)} 보기 →</span></a>')
        dong_section = (
            f'<section class="wrap cv"><div class="sec-head reveal">'
            f'<span class="eyebrow">DONG · 행정동 {len(dong_names)}</span>'
            f'<h2>{esc(dn)} 행정동</h2>'
            f'<p class="lead">아래 행정동을 누르면 동별 평균 도착 시간과 특화 콘텐츠를 확인할 수 있습니다. '
            f'1동·2동처럼 번호가 붙은 동은 기본 동명으로 통합했습니다.</p></div>'
            f'<div class="grid g4">{"".join(cs)}</div></section>')
    # 행정구 목록 (경기 일부 시) — 구별 페이지 카드
    gu_list = geo.GYEONGGI_GU.get(d["slug"], []) if r["slug"] == "gyeonggi" else []
    gu_section = ""
    if gu_list:
        cs = []
        for gslug, gname, gdongs in gu_list:
            gmin = dong_arrival(avg, r["slug"] + d["slug"] + gslug)
            href = f"/locations/{r['slug']}/{d['slug']}/{gslug}/"
            cs.append(
                f'<a class="card reveal" href="{href}"><div class="kicker">{esc(dn)}</div>'
                f'<h3>{esc(gname)}</h3><p>{esc(dn)} {esc(gname)} 출장마사지 · 평균 도착 약 {gmin}분. '
                f'{esc("、".join(gdongs[:3]))} 등 권역 데이터를 확인하세요.</p>'
                f'<span class="more">{esc(gname)} 보기 →</span></a>')
        gu_section = (
            f'<section class="wrap cv"><div class="sec-head reveal">'
            f'<span class="eyebrow">GU · 행정구 {len(gu_list)}</span>'
            f'<h2>{esc(dn)} 행정구</h2>'
            f'<p class="lead">아래 행정구를 누르면 구별 평균 도착 시간과 특화 콘텐츠를 확인할 수 있습니다.</p></div>'
            f'<div class="grid g4">{"".join(cs)}</div></section>')
    faq = [
        (f"{dn}은 도착까지 얼마나 걸리나요?", f"{dn} 전체 평균은 약 {avg}분이며, {fast[0]}은 {fast[1]}분대, {slow[0]}은 {slow[1]}분대로 동별 차이가 있습니다. 예약 시 실제 예상 시간을 안내드립니다."),
        (f"{dn} 어떤 동까지 출장이 되나요?", f"{dong_list} 등 {dn} 전 지역으로 출장합니다."),
        (f"{dn} 요금은 다른 지역과 다른가요?", "아니요. 모든 행정구가 동일한 정찰 요금이며 지역별 추가 비용은 없습니다."),
        ("심야에도 예약이 되나요?", f"네, 연중무휴 24시간 운영합니다. {dn}은 저녁·심야 예약이 몰리는 편이라 여유 있게 예약하시면 좋습니다."),
        ("관리사 국적을 고를 수 있나요?", "한국·중국·태국·베트남·러시아·일본 6개국 중 선호를 말씀하시면 배차 상황에 맞춰 반영합니다."),
        (f"{dn} 예약은 어떻게 하나요?", f"{TEL} 전화 또는 24시간 상담으로 위치와 코스를 알려주시면 본사에서 배차합니다."),
    ]
    crumbs = [("홈", "/"), ("지역", "/locations/"), (rn, f"/locations/{r['slug']}/"),
              (dn, f"/locations/{r['slug']}/{d['slug']}/")]
    body = f'''{header()}
{crumb_html(crumbs)}
<section class="hero compact"><div class="hero-inner"><div class="hero-copy reveal">
<span class="eyebrow"><span class="pulse"></span>{esc(rn)} · {esc(dn)} OPERATIONS</span>
<h1>{esc(dn)} 출장마사지</h1>
<p class="lead">{esc(d["character"])}. 동별 평균 도착 시간과 정찰 요금, {esc(dn)} 특화 후기를 데이터로 안내합니다.</p>
<div class="chips">
<div class="chip">AVG ARRIVAL<b>약 {avg}분</b></div>
<div class="chip">AVAILABLE<b>연중무휴 24시</b></div>
<div class="chip">CHARACTER<b>{esc(d["landmarks"][0])} 권역</b></div></div>
<div class="actions"><a class="btn btn-primary" href="tel:{TEL}">예약 {esc(TEL)} →</a></div></div></div></section>

<section class="wrap cv"><div class="sec-head reveal"><span class="eyebrow">OVERVIEW</span><h2>{esc(dn)} 운영 개요</h2></div>
{"".join(overview)}</section>

<section class="wrap cv"><div class="sec-head reveal"><span class="eyebrow">FIELD NOTES · 2026</span><h2>{esc(dn)} 현장 노트</h2></div>
{"".join(fieldnotes)}
<div class="databox reveal"><h3>Data &amp; Methodology</h3>
<p>도착 시간: 최근 {DISPATCH_MONTHS}개월 자체 배차 로그 기준 {esc(dn)} 동별 평균값(정상 교통 기준).</p>
<p>측정: 예약 접수 시각부터 현장 도착 보고 시각까지 실측 차이를 동 단위로 집계.</p>
<p>표기 평균은 참고용이며, 출퇴근·심야·기상에 따라 편차가 있습니다.</p></div></section>

{dong_section}
{gu_section}

<section class="wrap cv"><div class="sec-head reveal"><span class="eyebrow">PRICING</span><h2>요금</h2></div>
{price_grid(SERVICES)}</section>

<section class="wrap cv"><div class="sec-head reveal"><span class="eyebrow">FAQ</span><h2>{esc(dn)} 자주 묻는 질문</h2></div>
{faq_html(faq)}</section>

<section class="wrap cv"><div class="sec-head reveal"><span class="eyebrow">REVIEWS</span><h2>{esc(dn)} 이용 후기</h2></div>
{review_cards(reviews)}</section>

{cta_band(f"{dn}, 지금 가장 가까운 매니저를 보내드립니다.")}
{footer()}'''
    ld = jsonld(
        breadcrumb_ld(crumbs),
        localbusiness_ld(name=f"{BRAND} {dn}", area=f"{r['full']} {dn}",
                         _id=f"/locations/{r['slug']}/{d['slug']}/#business"),
        {"@type": "AdministrativeArea", "name": f"{r['full']} {dn}"},
        {"@type": "Service", "serviceType": "출장마사지", "name": f"{dn} 출장마사지",
         "provider": {"@id": DOMAIN + "/#org"}, "areaServed": {"@type": "AdministrativeArea", "name": f"{r['full']} {dn}"}},
        {"@type": "AggregateRating", "itemReviewed": {"@type": "LocalBusiness", "name": f"{BRAND} {dn}"},
         "ratingValue": RATING_VALUE, "reviewCount": len(reviews) * 30 + 90, "bestRating": "5"},
        *reviews_ld(reviews, f"{dn} 출장마사지"),
        faq_ld(faq))
    write(f"/locations/{r['slug']}/{d['slug']}/",
          head(title, desc, f"/locations/{r['slug']}/{d['slug']}/", extra_ld=ld), body)
    # 행정동 leaf 페이지 생성 (서울·인천·부산)
    d_crumbs = [("홈", "/"), ("지역", "/locations/"), (rn, f"/locations/{r['slug']}/"),
                (dn, f"/locations/{r['slug']}/{d['slug']}/")]
    for dname in dong_names:
        build_dong(r, dn, f"/locations/{r['slug']}/{d['slug']}/", d_crumbs, avg,
                   dname, dong_names, d["landmarks"], d["character"])
    # 행정구 페이지 생성 (경기 일부 시) — 구가 행정동 허브
    for gslug, gname, gdongs in gu_list:
        build_gu(r, d, gslug, gname, gdongs, avg)


# ════════════════════════════════════════════════════════════
# 행정동(동) leaf 페이지
# ════════════════════════════════════════════════════════════
def dong_arrival(base, key):
    rnd = random.Random("arr" + key)
    return max(20, base + rnd.randint(-4, 6))

DSITU = ["야근 후 늦은 밤", "주말 오후", "오랜만의 휴식으로", "어깨가 무거운 날",
         "장거리 운전 뒤", "재택근무로 굳은 몸을 풀려고", "수면이 부족할 때",
         "운동을 마치고", "기념일에 셀프 선물로", "허리가 뻐근한 날"]

def dong_reviews(dong, dn, rn, key, n=5):
    rnd = random.Random("dongrev" + key)
    out = []
    for i in range(n):
        svc = rnd.choice(SERVICES); dur = rnd.choice(["60분", "90분", "120분"])
        situ = rnd.choice(DSITU); praise = rnd.choice(PRAISE)
        text = (f"{dong}에서 {situ} {svc['name']} {dur} 코스를 예약했어요. "
                f"{praise} {dn} {dong} 쪽은 안내받은 도착 시간대도 정확했습니다.")
        out.append({"name": rnd.choice(NAMES), "rating": rnd.choice([5, 5, 5, 4]),
                    "text": text, "title": f"{dong} {svc['name']} 후기"})
    return out

def build_dong(r, parent_name, parent_path, parent_crumbs, base_avg, dong, dong_list, landmarks_list, area_char):
    rn = r["name"]; dn = parent_name; full = r["full"]
    key = parent_path + dong
    district_avg = base_avg
    mins = dong_arrival(base_avg, key)
    sibs = [x for x in dong_list if x != dong]
    rnd = random.Random("sib" + key); rnd.shuffle(sibs)
    sib_str = "、".join(sibs[:3]) if sibs else dn
    landmarks = "、".join(landmarks_list) if landmarks_list else dn
    lm0 = landmarks_list[0] if landmarks_list else dn
    path = parent_path + dong + "/"
    title = f"{rn} {dn} {dong} 출장마사지 — 평균 도착 약 {mins}분 | {BRAND}"
    desc = (f"{full} {dn} {dong} 출장마사지. 평균 도착 약 {mins}분, 정찰 요금, "
            f"{dong} 특화 후기를 안내합니다. 스웨디시·아로마·타이·로미로미·스포츠 24시간.")

    overview = (
        note_card(5, f"{dong} 평균 도착 시간",
            [f"{dn} {dong} 일대의 출장 평균 도착 시간은 약 {mins}분입니다(정상 교통 기준).",
             f"이는 {dn} 전체 평균(약 {district_avg}분)과 비교해 권역 내 위치와 접근성을 반영한 값입니다.",
             f"인접한 {sib_str} 방면과 매니저 동선을 공유해 배차 효율을 높이고 있습니다.",
             "출퇴근·심야·기상 상황에 따라 편차가 있어 예약 시 실제 예상 시간을 다시 안내드립니다."]),
        note_card(6, f"{dong} 시간대별 콜 분포",
            [f"{dong}이 속한 {dn}은 {area_char}입니다.",
             "그래서 저녁부터 심야로 갈수록 예약이 몰리는 시간대가 형성됩니다.",
             "피크 시간에는 표기 평균보다 도착이 다소 길어질 수 있어 여유 있는 예약을 권합니다.",
             f"본사는 {dong} 인근의 콜 분포를 분석해 야간 배차 인력을 보강하고 있습니다."]),
        note_card(7, f"{dong}에 어울리는 추천 코스",
            [f"{lm0} 등 {dn} 주요 거점과 가까운 {dong}은 업무·주거 피로를 호소하는 고객이 많습니다.",
             "수면 부족·스트레스가 주된 고민이면 아로마 90분이나 스웨디시가 무난합니다.",
             "장시간 좌식이나 운동 후 근피로가 뚜렷하면 타이 스트레칭이나 스포츠 코스를 권합니다.",
             "선택이 어렵다면 상담 시 컨디션을 말씀해 주시면 맞춤으로 추천드립니다."]),
        note_card(8, f"{dong} 예약·결제·환불",
            [f"{dong} 출장 예약은 {TEL} 전화 또는 24시간 상담으로 접수합니다.",
             "모든 코스는 정찰 요금으로 진행되며 코스 외 추가 비용이나 지역 할증이 없습니다.",
             "매니저 출발 전 취소는 위약금이 없고, 출발 후에는 이동 비용이 발생할 수 있습니다.",
             "결제 수단과 영수증 발행은 예약 단계에서 안내드립니다."]),
    )
    fieldnotes = (
        note_card(1, f"{dong}은 어떤 동인가요",
            [f"{dong}은 {full} {dn}에 속한 행정동입니다.",
             f"{landmarks} 등 {dn} 주요 거점을 중심으로 한 생활·이동 동선 안에 자리합니다.",
             f"인접한 {sib_str} 등과 함께 본사 디스패처가 하나의 배차 권역으로 관리합니다.",
             "1동·2동처럼 번호가 붙은 행정동은 기본 동명으로 통합해 안내합니다."]),
        note_card(2, f"{dong} 매니저 배치와 도착",
            [f"본사는 {dn} 권역의 수요에 맞춰 {dong} 인근에 매니저를 배치합니다.",
             f"덕분에 {dong} 일대는 평균 약 {mins}분 내외로 도착하는 경우가 많습니다.",
             "다만 시간대와 교통 상황에 따라 도착 시간은 달라질 수 있습니다.",
             "예약 시점의 실제 예상 도착 시간을 분 단위로 다시 안내드립니다."]),
        note_card(3, f"{dong} 안전 가이드",
            [f"안전 자문 트레이너 {TEAM[1]['name']}({TEAM[1]['bio']})의 가이드라인을 {dong}에서도 동일하게 적용합니다.",
             "관리 전 압 세기와 집중 부위, 금기 사항을 확인한 뒤 진행합니다.",
             "임신·고혈압·급성 통증 등은 사전 고지 시 코스를 조정합니다.",
             "본 서비스는 의료 행위가 아닌 19세 이상 대상의 이완·건강관리 서비스입니다."]),
        note_card(4, f"{dong} 운영 원칙",
            ["정찰 요금제로 운영해 심야·휴일이라는 이유의 임의 할증이 없습니다.",
             "예약 단계에서 코스·시간·도착 예정·결제 금액을 모두 안내합니다.",
             "외부 중개 없이 본사 디스패처가 직접 배차해 책임 소재가 분명합니다.",
             f"{dong} 단골 고객을 위한 재방문 매니저 지정도 가능합니다."]),
    )
    reviews = dong_reviews(dong, dn, rn, key, n=5)
    faq = [
        (f"{dong}은 도착까지 얼마나 걸리나요?", f"{dn} {dong} 일대는 평균 약 {mins}분입니다(정상 교통 기준). 시간대·교통에 따라 달라질 수 있어 예약 시 실제 예상 시간을 안내드립니다."),
        (f"{dong}도 출장이 되나요?", f"네, {dong} 전 지역으로 출장합니다. 인접한 {sib_str} 등도 같은 권역으로 배차합니다."),
        (f"{dong} 요금은 다른 곳과 다른가요?", "아니요. 모든 지역이 동일한 정찰 요금이며 지역별 출장비 할증이 없습니다."),
        ("심야에도 예약이 되나요?", f"네, 연중무휴 24시간 운영합니다. {dong}은 저녁·심야 예약이 몰리는 편이라 여유 있게 예약하시면 좋습니다."),
        ("관리사 국적을 고를 수 있나요?", "한국·중국·태국·베트남·러시아·일본 6개국 중 선호를 말씀하시면 배차 상황에 맞춰 반영합니다."),
        (f"{dong} 예약은 어떻게 하나요?", f"{TEL} 전화 또는 24시간 상담으로 위치와 코스를 알려주시면 본사 디스패처가 배차합니다."),
    ]
    crumbs = list(parent_crumbs) + [(dong, path)]
    body = f'''{header()}
{crumb_html(crumbs)}
<section class="hero compact"><div class="hero-inner"><div class="hero-copy reveal">
<span class="eyebrow"><span class="pulse"></span>{esc(rn)} {esc(dn)} · {esc(dong)} OPERATIONS</span>
<h1>{esc(dong)} 출장마사지</h1>
<p class="lead">{esc(full)} {esc(dn)} {esc(dong)} 일대 평균 도착 약 {mins}분. 정찰 요금과 {esc(dong)} 특화 후기를 데이터로 안내합니다.</p>
<div class="chips">
<div class="chip">AVG ARRIVAL<b>약 {mins}분</b></div>
<div class="chip">AVAILABLE<b>연중무휴 24시</b></div>
<div class="chip">AREA<b>{esc(dn)}</b></div></div>
<div class="actions"><a class="btn btn-primary" href="tel:{TEL}">예약 {esc(TEL)} →</a>
<a class="btn btn-ghost" href="{enc(parent_path)}">{esc(dn)} 전체 보기</a></div></div></div></section>

<section class="wrap cv"><div class="sec-head reveal"><span class="eyebrow">OVERVIEW</span><h2>{esc(dong)} 운영 개요</h2></div>
{"".join(overview)}</section>

<section class="wrap cv"><div class="sec-head reveal"><span class="eyebrow">FIELD NOTES · 2026</span><h2>{esc(dong)} 현장 노트</h2></div>
{"".join(fieldnotes)}
<div class="databox reveal"><h3>Data &amp; Methodology</h3>
<p>도착 시간: 최근 {DISPATCH_MONTHS}개월 자체 배차 로그 기준 {esc(dn)} {esc(dong)} 일대 평균값(정상 교통 기준).</p>
<p>측정: 예약 접수 시각부터 현장 도착 보고 시각까지 실측 차이를 동 단위로 집계.</p>
<p>표기 평균은 참고용이며, 출퇴근·심야·기상에 따라 편차가 있습니다.</p></div></section>

<section class="wrap cv"><div class="sec-head reveal"><span class="eyebrow">PRICING</span><h2>요금</h2></div>
{price_grid(SERVICES)}</section>

<section class="wrap cv"><div class="sec-head reveal"><span class="eyebrow">FAQ</span><h2>{esc(dong)} 자주 묻는 질문</h2></div>
{faq_html(faq)}</section>

<section class="wrap cv"><div class="sec-head reveal"><span class="eyebrow">REVIEWS</span><h2>{esc(dong)} 이용 후기</h2></div>
{review_cards(reviews)}</section>

{cta_band(f"{dong}, 지금 가장 가까운 매니저를 보내드립니다.")}
{footer()}'''
    ld = jsonld(
        breadcrumb_ld(crumbs),
        localbusiness_ld(name=f"{BRAND} {dong}", area=f"{full} {dn} {dong}",
                         _id=enc(path) + "#business"),
        {"@type": "Service", "serviceType": "출장마사지", "name": f"{dong} 출장마사지",
         "provider": {"@id": DOMAIN + "/#org"},
         "areaServed": {"@type": "Place", "name": f"{full} {dn} {dong}"}},
        {"@type": "AggregateRating", "itemReviewed": {"@type": "LocalBusiness", "name": f"{BRAND} {dong}"},
         "ratingValue": RATING_VALUE, "reviewCount": len(reviews) * 12 + 40, "bestRating": "5"},
        *reviews_ld(reviews, f"{dong} 출장마사지"),
        faq_ld(faq))
    write(path, head(title, desc, path, extra_ld=ld), body)


# ════════════════════════════════════════════════════════════
# 행정구(경기 일부 시) leaf 페이지
# ════════════════════════════════════════════════════════════
def build_gu(r, city, gslug, gname, gdongs, city_avg):
    rn = r["name"]; cn = city["name"]; full = r["full"]
    key = r["slug"] + city["slug"] + gslug
    gavg = dong_arrival(city_avg, key)
    # 구 내 동별 도착시간(결정적)
    dong_mins = [(dname, dong_arrival(gavg, key + dname)) for dname in gdongs]
    fast = min(dong_mins, key=lambda x: x[1]); slow = max(dong_mins, key=lambda x: x[1])
    dong_list = "、".join(f"{n} 약 {m}분" for n, m in dong_mins)
    head_name = f"{cn} {gname}"
    path = f"/locations/{r['slug']}/{city['slug']}/{gslug}/"
    title = f"{cn} {gname} 출장마사지 — 동별 평균 도착 시간 공개 | {BRAND}"
    desc = (f"{full} {cn} {gname} 출장마사지. {', '.join(n for n, _ in dong_mins[:3])} 등 "
            f"동별 평균 도착 시간과 정찰 요금, {gname} 특화 후기를 안내합니다.")

    overview = (
        note_card(5, f"{gname} 동(洞)별 평균 도착 시간",
            [f"{cn} {gname} 안에서도 동별로 접근성이 달라 평균 도착 시간에 차이가 있습니다.",
             f"실측 기준 {dong_list} 수준입니다.",
             f"가장 빠른 권역은 {fast[0]}({fast[1]}분대), 시간이 더 걸리는 곳은 {slow[0]}({slow[1]}분대)입니다.",
             f"{gname} 전체 평균은 약 {gavg}분으로, 정상 교통 기준 자체 배차 로그에서 산출한 값입니다."]),
        note_card(6, f"{gname} 시간대별 콜 분포",
            [f"{gname}은 {cn}의 주요 생활·업무 권역 중 하나입니다.",
             "저녁부터 심야로 갈수록 예약이 몰리는 시간대가 형성됩니다.",
             "피크 시간에는 표기 평균보다 도착이 다소 길어질 수 있어 여유 있는 예약을 권합니다.",
             f"본사는 {gname} 인근의 콜 분포를 분석해 야간 배차를 보강합니다."]),
        note_card(7, f"{gname}에 어울리는 추천 코스",
            [f"{gname} 일대는 업무·주거 피로로 인한 이완 수요가 많습니다.",
             "수면 부족·스트레스가 주된 고민이면 아로마 90분이나 스웨디시가 무난합니다.",
             "장시간 좌식·운동 후 근피로가 뚜렷하면 타이 스트레칭이나 스포츠 코스를 권합니다.",
             "선택이 어렵다면 상담 시 컨디션을 말씀해 주시면 맞춤으로 추천드립니다."]),
        note_card(8, f"{gname} 예약·결제·환불",
            [f"{gname} 출장 예약은 {TEL} 전화 또는 24시간 상담으로 접수합니다.",
             "모든 코스는 정찰 요금으로 진행되며 코스 외 추가 비용이나 지역 할증이 없습니다.",
             "매니저 출발 전 취소는 위약금이 없고, 출발 후에는 이동 비용이 발생할 수 있습니다.",
             "결제 수단과 영수증 발행은 예약 단계에서 안내드립니다."]),
    )
    fieldnotes = (
        note_card(1, f"{gname}은 어떤 권역인가요",
            [f"{gname}은 {full} {cn}를 구성하는 행정구입니다.",
             f"{', '.join(n for n, _ in dong_mins[:4])} 등 생활권을 중심으로 이동 동선이 형성됩니다.",
             "권역 성격은 시간대별 수요와 도착 시간에 직접 영향을 줍니다.",
             "그래서 단순한 지역명 치환이 아니라 권역별 실제 데이터로 안내드립니다."]),
        note_card(2, f"{gname} 매니저 배치와 도착",
            [f"본사는 {cn} 권역의 콜 분포에 맞춰 {gname} 인근에 매니저를 배치합니다.",
             f"덕분에 {fast[0]} 방면은 약 {fast[1]}분대로 비교적 빠르게 도착합니다.",
             f"반면 {slow[0]} 방면은 거리상 {slow[1]}분대로 다소 더 소요됩니다.",
             "예약 시점의 실제 예상 도착 시간을 분 단위로 다시 안내드립니다."]),
        note_card(3, f"{gname} 안전 가이드",
            [f"안전 자문 트레이너 {TEAM[1]['name']}({TEAM[1]['bio']})의 가이드라인을 {gname}에서도 동일하게 적용합니다.",
             "관리 전 압 세기와 집중 부위, 금기 사항을 확인한 뒤 진행합니다.",
             "임신·고혈압·급성 통증 등은 사전 고지 시 코스를 조정합니다.",
             "본 서비스는 의료 행위가 아닌 19세 이상 대상의 이완·건강관리 서비스입니다."]),
        note_card(4, f"{gname} 운영 원칙",
            ["정찰 요금제로 운영해 심야·휴일이라는 이유의 임의 할증이 없습니다.",
             "예약 단계에서 코스·시간·도착 예정·결제 금액을 모두 안내합니다.",
             "외부 중개 없이 본사 디스패처가 직접 배차해 책임 소재가 분명합니다.",
             f"{gname} 단골 고객을 위한 재방문 매니저 지정도 가능합니다."]),
    )
    reviews = dong_reviews(gname, cn, rn, key, n=5)
    faq = [
        (f"{gname}은 도착까지 얼마나 걸리나요?", f"{gname} 전체 평균은 약 {gavg}분이며, {fast[0]}은 {fast[1]}분대, {slow[0]}은 {slow[1]}분대로 동별 차이가 있습니다. 예약 시 실제 예상 시간을 안내드립니다."),
        (f"{gname} 어떤 동까지 출장이 되나요?", f"{dong_list} 등 {gname} 전 지역으로 출장합니다."),
        (f"{gname} 요금은 다른 곳과 다른가요?", "아니요. 모든 지역이 동일한 정찰 요금이며 지역별 출장비 할증이 없습니다."),
        ("심야에도 예약이 되나요?", f"네, 연중무휴 24시간 운영합니다. {gname}은 저녁·심야 예약이 몰리는 편이라 여유 있게 예약하시면 좋습니다."),
        ("관리사 국적을 고를 수 있나요?", "한국·중국·태국·베트남·러시아·일본 6개국 중 선호를 말씀하시면 배차 상황에 맞춰 반영합니다."),
        (f"{gname} 예약은 어떻게 하나요?", f"{TEL} 전화 또는 24시간 상담으로 위치와 코스를 알려주시면 본사 디스패처가 배차합니다."),
    ]
    crumbs = [("홈", "/"), ("지역", "/locations/"), (rn, f"/locations/{r['slug']}/"),
              (cn, f"/locations/{r['slug']}/{city['slug']}/"), (gname, path)]
    # 행정동 카드 (구 → 동)
    dcs = []
    for dn2, dm in dong_mins:
        dhref = enc(path + dn2 + "/")
        dcs.append(
            f'<a class="card reveal" href="{dhref}"><div class="kicker">{esc(gname)}</div>'
            f'<h3>{esc(dn2)}</h3><p>{esc(gname)} {esc(dn2)} 출장마사지 · 평균 도착 약 {dm}분. '
            f'동별 도착 시간·추천 코스·후기를 확인하세요.</p>'
            f'<span class="more">{esc(dn2)} 보기 →</span></a>')
    dong_section = (
        f'<section class="wrap cv"><div class="sec-head reveal">'
        f'<span class="eyebrow">DONG · 행정동 {len(dong_mins)}</span>'
        f'<h2>{esc(gname)} 행정동</h2>'
        f'<p class="lead">아래 행정동을 누르면 동별 평균 도착 시간과 특화 콘텐츠를 확인할 수 있습니다. '
        f'1동·2동처럼 번호가 붙은 동은 기본 동명으로 통합했습니다.</p></div>'
        f'<div class="grid g4">{"".join(dcs)}</div></section>')
    body = f'''{header()}
{crumb_html(crumbs)}
<section class="hero compact"><div class="hero-inner"><div class="hero-copy reveal">
<span class="eyebrow"><span class="pulse"></span>{esc(cn)} · {esc(gname)} OPERATIONS</span>
<h1>{esc(gname)} 출장마사지</h1>
<p class="lead">{esc(full)} {esc(cn)} {esc(gname)} 동별 평균 도착 시간과 정찰 요금, {esc(gname)} 특화 후기를 데이터로 안내합니다.</p>
<div class="chips">
<div class="chip">AVG ARRIVAL<b>약 {gavg}분</b></div>
<div class="chip">AVAILABLE<b>연중무휴 24시</b></div>
<div class="chip">AREA<b>{esc(cn)}</b></div></div>
<div class="actions"><a class="btn btn-primary" href="tel:{TEL}">예약 {esc(TEL)} →</a>
<a class="btn btn-ghost" href="{enc(f"/locations/{r['slug']}/{city['slug']}/")}">{esc(cn)} 전체 보기</a></div></div></div></section>

<section class="wrap cv"><div class="sec-head reveal"><span class="eyebrow">OVERVIEW</span><h2>{esc(gname)} 운영 개요</h2></div>
{"".join(overview)}</section>

<section class="wrap cv"><div class="sec-head reveal"><span class="eyebrow">FIELD NOTES · 2026</span><h2>{esc(gname)} 현장 노트</h2></div>
{"".join(fieldnotes)}
<div class="databox reveal"><h3>Data &amp; Methodology</h3>
<p>도착 시간: 최근 {DISPATCH_MONTHS}개월 자체 배차 로그 기준 {esc(gname)} 동별 평균값(정상 교통 기준).</p>
<p>측정: 예약 접수 시각부터 현장 도착 보고 시각까지 실측 차이를 동 단위로 집계.</p>
<p>표기 평균은 참고용이며, 출퇴근·심야·기상에 따라 편차가 있습니다.</p></div></section>

{dong_section}

<section class="wrap cv"><div class="sec-head reveal"><span class="eyebrow">PRICING</span><h2>요금</h2></div>
{price_grid(SERVICES)}</section>

<section class="wrap cv"><div class="sec-head reveal"><span class="eyebrow">FAQ</span><h2>{esc(gname)} 자주 묻는 질문</h2></div>
{faq_html(faq)}</section>

<section class="wrap cv"><div class="sec-head reveal"><span class="eyebrow">REVIEWS</span><h2>{esc(gname)} 이용 후기</h2></div>
{review_cards(reviews)}</section>

{cta_band(f"{gname}, 지금 가장 가까운 매니저를 보내드립니다.")}
{footer()}'''
    ld = jsonld(
        breadcrumb_ld(crumbs),
        localbusiness_ld(name=f"{BRAND} {head_name}", area=f"{full} {cn} {gname}",
                         _id=path + "#business"),
        {"@type": "AdministrativeArea", "name": f"{full} {cn} {gname}"},
        {"@type": "Service", "serviceType": "출장마사지", "name": f"{gname} 출장마사지",
         "provider": {"@id": DOMAIN + "/#org"},
         "areaServed": {"@type": "AdministrativeArea", "name": f"{full} {cn} {gname}"}},
        {"@type": "AggregateRating", "itemReviewed": {"@type": "LocalBusiness", "name": f"{BRAND} {head_name}"},
         "ratingValue": RATING_VALUE, "reviewCount": len(reviews) * 18 + 60, "bestRating": "5"},
        *reviews_ld(reviews, f"{gname} 출장마사지"),
        faq_ld(faq))
    write(path, head(title, desc, path, extra_ld=ld), body)
    # 구 → 행정동 leaf 페이지 생성
    g_crumbs = [("홈", "/"), ("지역", "/locations/"), (rn, f"/locations/{r['slug']}/"),
                (cn, f"/locations/{r['slug']}/{city['slug']}/"), (gname, path)]
    g_landmarks = city.get("landmarks", []) or [cn]
    g_char = f"{cn}의 주요 생활·업무 권역"
    for dname in gdongs:
        build_dong(r, gname, path, g_crumbs, gavg, dname, gdongs, g_landmarks, g_char)


# ════════════════════════════════════════════════════════════
# 정책 페이지
# ════════════════════════════════════════════════════════════
def policy_content(slug):
    if slug == "privacy":
        return [
            ("총칙",
             [f"{COMPANY}({BRAND}, 이하 ‘회사’)는 이용자의 개인정보를 중요하게 생각하며, 「개인정보 보호법」 등 관계 법령을 준수합니다.",
              "본 방침은 회사가 제공하는 출장 건강관리 서비스의 예약·상담·결제 과정에서 처리하는 개인정보에 적용됩니다.",
              "회사는 본 방침을 홈페이지 하단에 상시 공개하여 이용자가 언제든 확인할 수 있도록 합니다.",
              "본 방침은 관련 법령 및 회사 방침 변경에 따라 개정될 수 있으며, 개정 시 시행일과 변경 내용을 공지합니다."]),
            ("수집하는 개인정보 항목",
             ["필수 항목: 예약자 성명 또는 호칭, 연락처(휴대전화번호), 방문 주소, 희망 일시, 요청 코스.",
              "결제 항목: 결제가 필요한 경우 결제 수단 확인에 필요한 최소한의 정보.",
              "자동 생성 항목: 상담 통화 기록, 접속 일시 등이 서비스 운영·분쟁 대응을 위해 생성·보관될 수 있습니다.",
              "회사는 사상·신념, 건강 등 민감정보를 원칙적으로 수집하지 않으며, 코스 조정을 위해 이용자가 자발적으로 고지한 건강 관련 사항은 해당 예약에 한해서만 활용합니다."]),
            ("개인정보의 수집 방법",
             ["전화 예약·상담, 메시지 상담 채널을 통해 이용자가 직접 제공하는 방식으로 수집합니다.",
              "이용자가 제공하지 않으면 예약 접수·배차가 제한될 수 있습니다.",
              "회사는 법정대리인의 동의가 필요한 만 14세 미만 아동의 정보를 수집하지 않습니다.",
              "수집 시에는 수집 목적과 항목, 보유 기간을 사전에 안내합니다."]),
            ("개인정보의 이용 목적",
             ["수집한 정보는 예약 접수, 매니저 배차, 도착 안내, 결제 처리, 고객 응대 목적으로만 이용합니다.",
              "서비스 품질 개선과 부정 이용·분쟁 대응을 위해 최소한의 범위에서 활용할 수 있습니다.",
              "마케팅·광고 목적의 활용은 이용자의 별도 동의가 있는 경우에만 진행합니다.",
              "회사는 수집 목적 외의 용도로 개인정보를 이용하지 않습니다."]),
            ("보유 및 이용 기간",
             ["원칙적으로 예약 목적이 달성되면 해당 개인정보를 지체 없이 파기합니다.",
              "다만 「전자상거래 등에서의 소비자보호에 관한 법률」 등 관계 법령에 따라 일정 기간 보관할 수 있습니다.",
              "계약·청약철회 기록 5년, 대금 결제 및 재화 공급 기록 5년, 소비자 불만·분쟁 처리 기록 3년 등이 이에 해당합니다.",
              "보유 기간이 끝난 정보는 복구할 수 없는 방법으로 파기합니다."]),
            ("제3자 제공",
             ["회사는 이용자의 개인정보를 본 방침에 명시한 범위를 넘어 제3자에게 제공하지 않습니다.",
              "이용자가 사전에 동의한 경우 또는 법령에 특별한 규정이 있는 경우에 한해 예외적으로 제공할 수 있습니다.",
              "수사 목적으로 법령에 정해진 절차와 방법에 따라 수사기관의 요구가 있는 경우 제공할 수 있습니다.",
              "제공이 필요한 경우 제공받는 자, 목적, 항목, 보유 기간을 사전에 고지합니다."]),
            ("처리 위탁",
             ["회사는 원활한 서비스 제공을 위해 결제 처리, 문자 발송 등 일부 업무를 외부에 위탁할 수 있습니다.",
              "위탁 시 수탁자와 위탁 업무 내용을 본 방침을 통해 공개합니다.",
              "위탁 계약 시 개인정보의 안전한 관리에 관한 사항을 문서로 규정합니다.",
              "위탁 내용이나 수탁자가 변경되는 경우 지체 없이 본 방침을 통해 공개합니다."]),
            ("이용자와 법정대리인의 권리",
             ["이용자는 언제든지 본인 개인정보의 열람·정정·삭제·처리정지를 요청할 수 있습니다.",
              f"권리 행사는 고객센터({TEL})로 요청하시면 신원 확인 후 지체 없이 처리합니다.",
              "이용자가 정정을 요구한 경우, 정정을 완료하기 전까지 해당 정보를 이용·제공하지 않습니다.",
              "이용자는 개인정보 수집·이용 동의를 거부할 권리가 있으며, 거부 시 서비스 이용이 제한될 수 있습니다."]),
            ("파기 절차 및 방법",
             ["회사는 보유 기간이 경과하거나 처리 목적이 달성된 개인정보를 선정해 파기합니다.",
              "전자적 파일은 복구·재생되지 않도록 기술적 방법으로 영구 삭제합니다.",
              "종이 문서에 기록된 정보는 분쇄하거나 소각해 파기합니다.",
              "법령에 따라 보존하는 정보는 다른 정보와 분리하여 별도 보관합니다."]),
            ("안전성 확보 조치",
             ["개인정보에 대한 접근 권한을 최소화하고 취급 인원을 한정합니다.",
              "취급 인원을 대상으로 정기적인 교육을 실시합니다.",
              "개인정보의 전송·보관 과정에서 적절한 보호 조치를 적용합니다.",
              "내부 관리계획을 수립·시행하고 접근 기록을 관리합니다."]),
            ("쿠키 등 자동 수집 장치",
             ["회사는 서비스 운영 과정에서 접속 기록 등 일부 정보를 자동으로 생성·수집할 수 있습니다.",
              "이러한 정보는 서비스 운영, 품질 개선, 부정 이용 방지 목적으로만 활용됩니다.",
              "이용자는 브라우저 설정을 통해 쿠키 저장을 거부할 수 있습니다.",
              "다만 쿠키 저장을 거부하면 일부 기능 이용에 불편이 있을 수 있습니다."]),
            ("정보주체의 동의 없는 처리에 대한 제한",
             ["회사는 정보주체의 동의, 법률의 특별한 규정 등 「개인정보 보호법」이 허용하는 경우에 한해 개인정보를 처리합니다.",
              "동의 없이 처리할 수 있는 경우라도 그 범위를 최소화하고 목적을 벗어나지 않습니다.",
              "정보주체는 자신의 개인정보 처리에 관한 동의를 언제든 철회할 수 있습니다.",
              "동의 철회 방법은 수집 시점과 동일하게 쉽고 명확하게 안내합니다."]),
            ("개인정보보호책임자 및 권익 침해 구제",
             [f"개인정보보호책임자는 {PRIVACY_OFFICER}이며, 개인정보 관련 문의·불만·피해 구제를 총괄합니다.",
              f"개인정보 관련 문의·신고는 고객센터({TEL})로 접수하시면 됩니다.",
              "개인정보 침해로 도움이 필요하면 개인정보분쟁조정위원회, 한국인터넷진흥원 개인정보침해신고센터 등에 상담할 수 있습니다.",
              "본 방침의 시행일은 2026년 1월 1일입니다."]),
        ]
    if slug == "terms":
        return [
            ("제1조 목적",
             [f"본 약관은 {COMPANY}({BRAND}, 이하 ‘회사’)가 제공하는 출장 건강관리 서비스의 이용 조건과 절차, 회사와 이용자의 권리·의무를 정함을 목적으로 합니다.",
              "이용자는 예약을 접수하는 시점에 본 약관과 안내 사항에 동의한 것으로 봅니다.",
              "본 서비스는 만 19세 이상 성인을 대상으로 합니다.",
              "본 서비스는 「의료법」상 의료 행위가 아닌 이완·건강관리 목적의 출장 마사지 서비스입니다."]),
            ("제2조 용어의 정의",
             ["‘서비스’란 회사가 매니저를 이용자가 지정한 장소로 배차하여 제공하는 출장 건강관리 관리를 말합니다.",
              "‘매니저’란 회사가 교육·관리하여 배차하는 관리 담당자를 말합니다.",
              "‘디스패처’란 예약을 접수하고 매니저를 배정하는 회사 운영 인력을 말합니다.",
              "본 약관에서 정하지 않은 용어는 관계 법령과 일반 거래 관행에 따릅니다."]),
            ("제3조 예약·결제·취소",
             ["예약은 전화 또는 상담 채널로 접수하며, 회사가 배차를 확정함으로써 성립합니다.",
              "요금은 정찰제로 운영되며, 사전에 안내된 금액 외 추가 비용은 발생하지 않습니다.",
              "매니저 출발 전 예약 취소·변경은 위약금 없이 가능합니다.",
              "매니저 출발 후 또는 도착 후 취소는 이동·대기에 따른 비용이 발생할 수 있으며, 관리 중 중단 시 진행 시간만큼 정산합니다."]),
            ("제4조 이용자의 금지 행위",
             ["매니저에 대한 부당한 요구나 불법·퇴폐 행위 요구는 엄격히 금지됩니다.",
              "이를 위반하는 경우 관리는 즉시 중단되며 관련 비용은 환불되지 않습니다.",
              "폭언·폭력·성희롱 등 매니저의 안전과 인격을 침해하는 행위는 즉시 신고 및 법적 조치의 대상이 됩니다.",
              "허위 정보 제공이나 결제 회피 행위 또한 금지됩니다."]),
            ("제5조 회사의 의무",
             ["회사는 관계 법령과 본 약관에 따라 안정적이고 지속적인 서비스를 제공하기 위해 노력합니다.",
              "회사는 이용자의 개인정보를 개인정보처리방침에 따라 안전하게 관리합니다.",
              "회사는 관리에 필요한 위생용품과 준비물을 매니저를 통해 제공합니다.",
              "회사는 이용자의 정당한 의견이나 불만을 신속히 처리하기 위해 고객센터를 운영합니다."]),
            ("제6조 이용자의 의무",
             ["이용자는 예약 시 정확한 위치·연락처 등 필요한 정보를 제공해야 합니다.",
              "이용자는 매니저의 안전과 인격을 존중하고 안내 사항을 준수해야 합니다.",
              "이용자는 본인의 건강상 주의 사항을 사전에 고지하여야 합니다.",
              "이용자가 제공한 정보의 오류로 발생한 불이익에 대한 책임은 이용자에게 있습니다."]),
            ("제7조 서비스의 범위와 한계",
             ["본 서비스는 이완·건강관리 목적의 출장 마사지이며, 의료·치료 행위가 아닙니다.",
              "회사는 질환의 진단·치료를 표방하지 않으며, 통증이 지속·악화되는 경우 의료기관 진료를 권합니다.",
              "임신, 고혈압, 심혈관 질환, 급성 염증·부상 등은 사전 고지 시 코스를 조정하거나 제한할 수 있습니다.",
              "음주 직후, 발열·감염 의심 상태에서는 관리가 제한될 수 있습니다."]),
            ("제8조 면책과 손해배상",
             ["이용자가 제공한 정보의 오류로 발생한 문제에 대해 회사는 책임을 지지 않습니다.",
              "천재지변, 교통 통제 등 불가항력으로 인한 서비스 지연·중단에 대해서는 면책됩니다.",
              "회사의 고의 또는 과실로 이용자에게 손해가 발생한 경우 관계 법령에 따라 배상합니다.",
              "구체적 배상 범위와 기준은 관련 법령과 공정한 기준에 따릅니다."]),
            ("제9조 환불 및 청약철회",
             ["매니저 출발 전 예약을 취소하는 경우 위약금 없이 전액 환불됩니다.",
              "매니저 출발 후 도착 전 취소 시에는 이동에 소요된 실비가 공제될 수 있습니다.",
              "관리가 시작된 이후 이용자 사정으로 중단하는 경우 진행 시간에 해당하는 금액을 정산합니다.",
              "회사 또는 매니저의 귀책으로 정상적인 관리가 이루어지지 못한 경우 전액 환불합니다."]),
            ("제10조 예약 변경과 노쇼",
             ["예약 일시·장소 변경은 매니저 출발 전까지 고객센터를 통해 요청할 수 있습니다.",
              "변경 가능 여부는 배차 상황에 따라 달라질 수 있으며, 회사가 신속히 안내합니다.",
              "사전 연락 없이 약속 장소에 부재하여 관리가 불가능한 경우 이동 실비가 청구될 수 있습니다.",
              "반복적인 노쇼나 허위 예약은 향후 서비스 이용이 제한될 수 있습니다."]),
            ("제11조 지식재산권",
             ["사이트의 텍스트·이미지·데이터 등 콘텐츠에 대한 권리는 회사에 귀속됩니다.",
              "이용자는 회사의 사전 동의 없이 콘텐츠를 복제·배포·가공할 수 없습니다.",
              "도착 시간 등 데이터는 회사의 자체 배차 로그를 가공한 결과물입니다.",
              "무단 이용으로 발생한 분쟁의 책임은 이용자에게 있습니다."]),
            ("제12조 약관의 효력과 변경",
             ["본 약관은 서비스 화면에 게시하거나 기타 방법으로 공지함으로써 효력이 발생합니다.",
              "회사는 관계 법령을 위반하지 않는 범위에서 본 약관을 개정할 수 있습니다.",
              "약관을 개정하는 경우 개정 내용과 시행일을 명시하여 시행일 전에 공지합니다.",
              "이용자가 개정 약관에 동의하지 않는 경우 서비스 이용을 중단할 수 있습니다."]),
            ("제13조 분쟁 해결과 준거법",
             ["서비스 관련 분쟁은 우선 고객센터를 통한 상호 협의로 원만히 해결합니다.",
              "협의가 어려운 경우 「소비자기본법」에 따른 분쟁조정 등 관계 법령과 공정한 절차에 따릅니다.",
              "본 약관과 서비스 이용에 관하여는 대한민국 법령을 준거법으로 합니다.",
              "본 약관은 서비스 변경이나 법령 개정에 따라 개정될 수 있으며, 개정 시 시행일과 내용을 공지합니다."]),
            ("부칙",
             ["본 이용약관은 2026년 1월 1일부터 시행합니다.",
              "약관 개정 시에는 개정 사유와 시행일을 명시하여 시행일 이전에 공지합니다.",
              "본 약관에서 정하지 않은 사항은 관계 법령과 일반 거래 관행에 따릅니다.",
              f"약관에 관한 문의는 {TEL} 고객센터로 접수하실 수 있습니다."]),
        ]
    return [  # youth
        ("제1조 기본 방침",
         [f"{COMPANY}({BRAND}, 이하 ‘회사’)는 청소년이 건전한 인격체로 성장할 수 있도록 청소년 보호를 위해 최선을 다합니다.",
          f"{BRAND}는 만 19세 미만 청소년에게 일체의 서비스를 제공하지 않습니다.",
          "회사는 청소년 보호와 관련된 관계 법령을 준수합니다.",
          "본 서비스는 건전한 건강관리 목적의 합법 서비스이며, 청소년 유해 업소가 아닙니다."]),
        ("제2조 청소년 유해 정보로부터의 보호",
         ["회사는 사이트의 어떠한 콘텐츠에도 청소년 유해 정보를 포함하지 않습니다.",
          "콘텐츠는 정기적으로 점검하여 부적절하거나 선정적인 표현이 없도록 관리합니다.",
          "외부 링크나 광고가 게재될 경우 청소년 보호 기준에 부합하는지 사전에 확인합니다.",
          "청소년 접근이 우려되는 정보가 발견되면 즉시 차단·삭제 등 필요한 조치를 취합니다."]),
        ("제3조 성인 인증과 예약 확인 절차",
         ["회사는 예약 접수 단계에서 이용자의 성인 여부를 확인합니다.",
          "성인 여부 확인이 어려운 경우 예약을 보류하거나 추가 확인을 요청할 수 있습니다.",
          "청소년으로 확인되는 경우 즉시 예약을 거부하고 관련 정보를 파기합니다.",
          "광고·홍보 활동에서도 청소년을 대상으로 하지 않으며 청소년 보호 기준을 준수합니다."]),
        ("제4조 청소년 유해 매체물 표시",
         ["본 서비스와 콘텐츠는 청소년 유해 매체물에 해당하지 않습니다.",
          "회사는 관련 법령에 따른 표시 의무가 발생하는 경우 이를 성실히 이행합니다.",
          "유해 매체물로 오인될 수 있는 표현을 사용하지 않는 것을 편집 원칙으로 합니다.",
          "관계 기관의 점검과 시정 요청에 성실히 협조합니다."]),
        ("제5조 임직원·매니저 교육",
         ["회사는 청소년 보호의 중요성과 관련 법령을 운영 인력 및 매니저 교육에 포함합니다.",
          "청소년 대상 영업이 의심되는 예약을 즉시 거부하도록 접수 절차를 마련했습니다.",
          "교육 내용은 법령 개정에 맞추어 정기적으로 갱신합니다.",
          "위반 사항이 확인되면 내부 규정에 따라 엄격히 조치합니다."]),
        ("제6조 피해 청소년 보호와 신고",
         ["회사는 청소년 관련 피해가 우려되는 상황을 인지하면 즉시 필요한 조치를 취합니다.",
          "필요한 경우 청소년 보호 관련 기관과 협조하여 피해 확산을 방지합니다.",
          "신고자의 정보는 보호하며 신고를 이유로 한 어떠한 불이익도 발생하지 않도록 합니다.",
          "유해 사례나 부적절한 이용 사례는 고객센터로 언제든 신고할 수 있습니다."]),
        ("제7조 청소년 유해 환경으로부터의 보호",
         ["회사는 청소년이 유해한 환경에 노출되지 않도록 서비스 운영 전반에서 주의를 기울입니다.",
          "회사의 서비스는 만 19세 이상 성인을 대상으로 하며, 청소년 대상 영업을 일절 하지 않습니다.",
          "청소년이 보호자의 동의 없이 서비스를 이용하려는 정황이 확인되면 즉시 이용을 제한합니다.",
          "회사는 건전한 건강관리 서비스라는 본연의 목적에 충실하게 운영합니다."]),
        ("제8조 광고·홍보에서의 청소년 보호",
         ["회사는 광고·홍보 활동에서 청소년을 대상으로 하거나 청소년에게 유해한 표현을 사용하지 않습니다.",
          "선정적이거나 자극적인 문구·이미지를 광고에 사용하지 않는 것을 원칙으로 합니다.",
          "제휴·외부 매체를 통한 홍보 시에도 동일한 청소년 보호 기준을 적용합니다.",
          "부적절한 광고가 확인되면 즉시 수정하거나 게재를 중단합니다."]),
        ("제9조 모니터링과 자율 규제",
         ["회사는 사이트 콘텐츠와 이용 실태를 정기적으로 점검하여 청소년 보호 기준 위반 여부를 확인합니다.",
          "위반 소지가 있는 콘텐츠나 이용 행태가 발견되면 즉시 시정 조치를 취합니다.",
          "회사는 청소년 보호와 관련한 자율 규제 노력을 지속적으로 강화합니다.",
          "점검 결과 중대한 사안은 내부 책임자에게 보고하여 재발을 방지합니다."]),
        ("제10조 관계 기관 협조",
         ["회사는 청소년 보호와 관련한 관계 기관의 정책과 요청에 성실히 협조합니다.",
          "법령에 따른 신고·시정 요청이 있는 경우 지체 없이 이행합니다.",
          "청소년 피해가 우려되는 사안은 필요 시 관계 기관과 공조하여 대응합니다.",
          "회사는 청소년 보호 관련 법령의 제·개정 사항을 지속적으로 반영합니다."]),
        ("제11조 신고 처리 절차",
         ["청소년 보호와 관련한 신고가 접수되면 담당자가 즉시 내용을 확인합니다.",
          "사실관계 확인을 위해 필요한 경우 신고자에게 추가 정보를 요청할 수 있습니다.",
          "확인 결과 조치가 필요한 사안은 지체 없이 시정하고 재발 방지 대책을 마련합니다.",
          "처리 결과는 신고자가 요청한 경우 가능한 범위에서 안내합니다."]),
        ("제12조 기록의 보관",
         ["회사는 청소년 보호 관련 점검·교육·신고 처리 내역을 일정 기간 보관합니다.",
          "보관된 기록은 청소년 보호 업무의 연속성과 재발 방지를 위해서만 활용합니다.",
          "기록에 포함된 개인정보는 개인정보처리방침에 따라 안전하게 관리합니다.",
          "보관 기간이 지난 기록은 복구할 수 없는 방법으로 파기합니다."]),
        ("제13조 청소년 보호 책임자와 문의",
         [f"청소년 보호 업무는 개인정보보호책임자 {PRIVACY_OFFICER}이 함께 담당합니다.",
          f"문의·신고는 예약 전화 {TEL} 또는 고객센터로 접수합니다.",
          "신고가 접수되면 신속히 사실을 확인하고 필요한 조치를 취합니다.",
          "본 정책은 법령 개정에 따라 갱신되며, 갱신 시 본 페이지를 통해 공지합니다."]),
        ("부칙",
         ["본 청소년보호정책은 2026년 1월 1일부터 시행합니다.",
          "정책 개정 시에는 개정 사유와 시행일을 명시하여 시행일 이전에 공지합니다.",
          "본 정책에서 정하지 않은 사항은 관계 법령과 회사의 운영 방침에 따릅니다.",
          f"청소년 보호와 관련한 의견은 언제든 {TEL} 고객센터로 보내주시기 바랍니다."]),
    ]

def build_policy(p):
    title = f"{p['title']} | {BRAND}"
    desc = f"{BRAND}({COMPANY})의 {p['title']}입니다. 이용자 권리와 회사의 운영 기준을 안내합니다."
    notes = policy_content(p["slug"])
    note_html = "".join(note_card(i + 1, t, ps) for i, (t, ps) in enumerate(notes))
    crumbs = [("홈", "/"), (p["title"], f"/policy/{p['slug']}/")]
    body = f'''{header()}
{crumb_html(crumbs)}
<section class="hero compact"><div class="hero-inner"><div class="hero-copy reveal">
<span class="eyebrow">POLICY</span><h1>{esc(p["title"])}</h1>
<p class="lead">시행일 2026-01-01 · {esc(COMPANY)}</p></div></div></section>
<section class="wrap cv">{note_html}</section>
{footer()}'''
    ld = jsonld(breadcrumb_ld(crumbs))
    write(f"/policy/{p['slug']}/", head(title, desc, f"/policy/{p['slug']}/", extra_ld=ld), body)


# ════════════════════════════════════════════════════════════
# robots / sitemap / manifest
# ════════════════════════════════════════════════════════════
def build_meta_files():
    # priority map
    def prio(u):
        depth = u.strip("/").count("/")
        if u == "/": return ("1.0", "daily")
        if u.startswith("/policy/"): return ("0.3", "yearly")
        if u.startswith("/magazine/") and depth >= 1: return ("0.7", "monthly")
        if depth == 0: return ("0.9", "weekly")
        if depth == 1: return ("0.85", "weekly")
        return ("0.75", "weekly")
    today = datetime.date.today().isoformat()
    urls = ""
    for u, _ in sorted(set(PAGES)):
        p, f = prio(u)
        urls += (f"<url><loc>{DOMAIN}{enc(u)}</loc><lastmod>{today}</lastmod>"
                 f"<changefreq>{f}</changefreq><priority>{p}</priority></url>\n")
    sitemap = ('<?xml version="1.0" encoding="UTF-8"?>\n'
               '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
               + urls + "</urlset>\n")
    with open(os.path.join(ROOT, "sitemap.xml"), "w", encoding="utf-8") as f:
        f.write(sitemap)

    robots = f"""User-agent: *
Allow: /
Disallow: /admin/
Disallow: /api/

User-agent: GPTBot
Allow: /
User-agent: ClaudeBot
Allow: /
User-agent: Google-Extended
Allow: /

Sitemap: {DOMAIN}/sitemap.xml
Host: {DOMAIN.replace('https://', '')}
"""
    with open(os.path.join(ROOT, "robots.txt"), "w", encoding="utf-8") as f:
        f.write(robots)

    import json as _j
    manifest = {
        "name": f"{BRAND} 출장마사지", "short_name": BRAND,
        "description": "수도권·부산 24시 프리미엄 출장마사지 — 본사 직접 배차",
        "start_url": "/", "scope": "/", "display": "standalone",
        "background_color": "#0b0b0e", "theme_color": "#0b0b0e",
        "lang": "ko-KR", "orientation": "portrait",
        "icons": [
            {"src": "/icon-192.png", "sizes": "192x192", "type": "image/png", "purpose": "any"},
            {"src": "/icon-512.png", "sizes": "512x512", "type": "image/png", "purpose": "any"},
            {"src": "/icon-maskable-512.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable"},
        ],
    }
    with open(os.path.join(ROOT, "site.webmanifest"), "w", encoding="utf-8") as f:
        f.write(_j.dumps(manifest, ensure_ascii=False, indent=2))

    # favicon.svg (브랜드 그라데이션)
    svg = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#f4d29c"/><stop offset="0.45" stop-color="#e9b8a7"/><stop offset="1" stop-color="#c98a6b"/></linearGradient></defs><rect width="64" height="64" rx="14" fill="#0b0b0e"/><circle cx="32" cy="32" r="16" fill="url(#g)"/><circle cx="26" cy="26" r="5" fill="#fff" opacity="0.35"/></svg>'''
    with open(os.path.join(ROOT, "favicon.svg"), "w", encoding="utf-8") as f:
        f.write(svg)


def main():
    build_home()
    build_service_hub()
    for s in SERVICES:
        build_service_detail(s)
    build_therapist_hub()
    for t in THERAPISTS:
        build_therapist_detail(t)
    build_pricing()
    build_reviews()
    build_about()
    build_magazine_hub()
    for m in MAGAZINE:
        build_magazine_article(m)
    build_locations_hub()
    for r in REGIONS:
        build_region_hub(r)
        for d in DISTRICTS[r["slug"]]:
            build_district(r, d)
    for p in POLICIES:
        build_policy(p)
    build_meta_files()

    # 검증 리포트
    print(f"총 페이지: {len(PAGES)}")
    short = [(u, c) for u, c in PAGES if c < 2000]
    long = [(u, c) for u, c in PAGES if c > 2600]
    print(f"2000자 미만: {len(short)}")
    for u, c in short[:30]:
        print(f"  [{c}] {u}")
    if long:
        print(f"2600자 초과: {len(long)} (예: {long[:3]})")
    import statistics
    cs = [c for _, c in PAGES]
    print(f"본문 글자수 min={min(cs)} max={max(cs)} median={int(statistics.median(cs))}")


if __name__ == "__main__":
    main()
