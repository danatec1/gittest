(async () => {
  const keyword = "산업통상부";
  const results = [];

  function parseNumber(text) {
    const m = text.match(/(\d[\d,]*)/);
    return m ? Number(m[1].replaceAll(",", "")) : null;
  }

  function cleanLines(text) {
    return text.split("\n").map(v => v.trim()).filter(Boolean);
  }

  function isNoise(line) {
    return [
      "조회수", "다운로드", "활용신청", "수정일", "제공기관", "키워드", "페이지"
    ].some(k => line.includes(k));
  }

  function parseRows(html, pageNo) {
    const doc = new DOMParser().parseFromString(html, "text/html");
    const lines = cleanLines(doc.body.innerText);
    const rows = [];

    for (let i = 0; i < lines.length; i++) {
      const title = lines[i];
      if (title.length < 4 || isNoise(title)) continue;

      let viewCount = null;
      let metricName = null;
      let metricValue = null;

      for (let j = i + 1; j < Math.min(i + 16, lines.length); j++) {
        const line = lines[j];
        if (line.includes("조회수")) viewCount = parseNumber(line);
        if (line.includes("다운로드")) {
          metricName = "다운로드";
          metricValue = parseNumber(line);
        }
        if (line.includes("활용신청")) {
          metricName = "활용신청";
          metricValue = parseNumber(line);
        }
        if (viewCount !== null && metricName && metricValue !== null) {
          rows.push({
            data_type: metricName === "다운로드" ? "파일데이터" : "오픈API",
            title,
            view_count: viewCount,
            metric_name: metricName,
            metric_value: metricValue,
            keyword,
            page_no: pageNo,
          });
          break;
        }
      }
    }

    return rows;
  }

  async function fetchPage(page) {
    const body = new URLSearchParams({
      keyword,
      page: String(page),
      pageSize: "10"
    });

    const res = await fetch("https://www.data.go.kr/tcs/dss/selectDataSetList.do", {
      method: "POST",
      headers: {
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"
      },
      body: body.toString(),
      credentials: "include"
    });

    return await res.text();
  }

  for (let page = 1; page <= 30; page++) {
    const html = await fetchPage(page);
    const rows = parseRows(html, page);
    if (!rows.length) break;
    results.push(...rows);
  }

  const dedup = Array.from(
    new Map(results.map(r => [`${r.data_type}__${r.title}`, r])).values()
  );

  console.table(dedup);
})();
