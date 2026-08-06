/* Minimal EN/HI dictionary for key UI strings. */
const I18N = {
  en: {},  /* English strings live in the HTML itself */
  hi: {
    govIndia: "भारत सरकार", skipMain: "मुख्य सामग्री पर जाएं", screenReader: "स्क्रीन रीडर एक्सेस",
    ministry: "कॉर्पोरेट कार्य मंत्रालय", portalName: "पीएम इंटर्नशिप योजना पोर्टल",
    studentPortal: "छात्र पोर्टल", adminConsole: "एडमिन कंसोल", help: "सहायता",
    dashboard: "डैशबोर्ड", explore: "इंटर्नशिप खोजें", myApplications: "मेरे आवेदन", profile: "प्रोफ़ाइल",
    overview: "अवलोकन", students: "छात्र", listings: "लिस्टिंग",
    welcomeBack: "वापसी पर स्वागत है", completeProfile: "प्रोफ़ाइल पूर्ण करें →",
    activeApplications: "सक्रिय आवेदन", activeOffers: "सक्रिय ऑफ़र", offerWindow: "ऑफ़र प्रतिक्रिया अवधि",
    permitted: "अनुमत", daysLeft: "दिन शेष",
    recommendedForYou: "आपके लिए अनुशंसित", allSectors: "सभी क्षेत्र",
    searchPlaceholder: "भूमिका, कंपनी या कौशल से खोजें",
    applicationTimeline: "आवेदन समयरेखा", howMatches: "ATLAS आपको कैसे मिलाता है",
    comingSoon: "जल्द आ रहा है", gigWork: "गिग वर्क", studentNews: "छात्र समाचार",
    hackathons: "हैकाथॉन", schemes: "योजनाएं",
    exploreTitle: "इंटर्नशिप खोजें", search: "खोजें",
    profileSetup: "प्रोफ़ाइल सेटअप", saveProfile: "प्रोफ़ाइल सहेजें",
    fSkills: "कौशल (अल्पविराम से अलग)", fQualification: "योग्यता",
    fLocations: "पसंदीदा स्थान", fSectors: "पसंदीदा क्षेत्र", fTier: "कॉलेज टियर",
    fFirstGen: "पहली पीढ़ी के कॉलेज छात्र",
    nationalOverview: "राष्ट्रीय आवंटन अवलोकन", runAllocation: "आवंटन इंजन चलाएं",
    studentsTitle: "छात्र और आवंटन", listingsTitle: "इंटर्नशिप लिस्टिंग",
    addInternship: "+ नई इंटर्नशिप जोड़ें", saveInternship: "इंटर्नशिप सहेजें",
    applyNow: "अभी आवेदन करें", moreDetails: "अधिक विवरण",
    viewReasoning: "मिलान कारण देखें ▼", hideReasoning: "मिलान कारण छिपाएं ▲",
    chatTitle: "ATLAS सहायक", chatPh: "इंटर्नशिप, वजीफा, पात्रता के बारे में पूछें...", send: "भेजें",
    footerTitle: "ATLAS आवंटन पोर्टल", theScheme: "योजना", support: "सहायता", legal: "कानूनी",
    aboutPmis: "PMIS के बारे में", eligibility: "पात्रता", guidelines: "दिशानिर्देश",
    grievance: "शिकायत निवारण", contactUs: "संपर्क करें",
    terms: "नियम और शर्तें", privacy: "गोपनीयता नीति",
  },
};

let currentLang = "en";
const htmlDefaults = {};

function applyLang(lang) {
  currentLang = lang;
  document.querySelectorAll("[data-i18n]").forEach((el) => {
    const key = el.dataset.i18n;
    if (!(key in htmlDefaults)) htmlDefaults[key] = el.innerHTML;
    if (lang === "en") el.innerHTML = htmlDefaults[key];
    else if (I18N.hi[key]) el.innerHTML = I18N.hi[key];
  });
  document.querySelectorAll("[data-i18n-ph]").forEach((el) => {
    const key = el.dataset.i18nPh;
    if (!(key + "_ph" in htmlDefaults)) htmlDefaults[key + "_ph"] = el.placeholder;
    if (lang === "en") el.placeholder = htmlDefaults[key + "_ph"];
    else if (I18N.hi[key]) el.placeholder = I18N.hi[key];
  });
  document.getElementById("lang-en").classList.toggle("active", lang === "en");
  document.getElementById("lang-hi").classList.toggle("active", lang === "hi");
}

function t(key, fallback) {
  if (currentLang === "hi" && I18N.hi[key]) return I18N.hi[key];
  return fallback;
}

document.getElementById("lang-en").addEventListener("click", () => applyLang("en"));
document.getElementById("lang-hi").addEventListener("click", () => applyLang("hi"));
