:root {
  --vh: 100vh;

  --bgTop: #27384b;
  --bgMid: #1d2b3a;
  --bgBot: #16212d;

  --accent1: #5aaeff;
  --accent2: #3496ff;

  --text: #f7fbff;
}

/* Черная тема */
:root[data-theme="black"]{
  --bgTop:#1b2430;
  --bgMid:#141b24;
  --bgBot:#0e141c;
  --accent1:#8bb8ff;
  --accent2:#5a98ff;
}

/* Светлая тема - только выбор языка/цвета как было, + серая обводка кнопок */
:root[data-theme="light"]{
  --bgTop:#e8edf5;
  --bgMid:#d9e0eb;
  --bgBot:#cad1de;
  --accent1:#3a8cff;
  --accent2:#1a6cff;
  --text:#1a2634;
  
  /* Сёрая обводка как в WhatsApp */
  --btn-border: rgba(0, 0, 0, 0.12);
}

* {
  box-sizing: border-box;
  -webkit-tap-highlight-color: transparent;
}

html, body {
  height: 100%;
  margin: 0;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Inter, Arial, sans-serif;
  overflow: hidden;
  overscroll-behavior: none;
  touch-action: manipulation;
  -webkit-text-size-adjust: 100%;
}

body {
  position: relative;
  background: transparent;
  background-color: var(--bgBot);
  color: var(--text);
  display: flex;
  flex-direction: column;
  height: var(--vh);
  overflow: hidden;
}

body::after {
  content: "";
  position: fixed;
  inset: 0;
  pointer-events: none;
  z-index: 0;
  background:
    linear-gradient(180deg, var(--bgTop) 0%, var(--bgMid) 48%, var(--bgBot) 100%);
  background-repeat: no-repeat;
  background-color: var(--bgBot);
  filter: none;
}

body > * {
  position: relative;
  z-index: 2;
}

/* ========================= */
/* КУБИКИ - НЕ ТРОГАЕМ */
/* ========================= */
.cube {
  position: absolute;
  width: 108px;
  height: 108px;
  border-radius: 18px;

  background: color-mix(in srgb, var(--accent1) 18%, white 10%);
  border: 1px solid color-mix(in srgb, var(--accent1) 42%, white 20%);
  backdrop-filter: blur(8px) saturate(120%);
  -webkit-backdrop-filter: blur(8px) saturate(120%);
  box-shadow:
    0 8px 20px rgba(0,0,0,.08),
    0 0 18px color-mix(in srgb, var(--accent1) 22%, transparent);
  pointer-events: none;
  opacity: .72;
}

.cube.small {
  width: 56px;
  height: 56px;
  border-radius: 14px;
  opacity: .52;
}

.cube.tiny {
  width: 30px;
  height: 30px;
  border-radius: 10px;
  opacity: .38;
}

/* анимации */
.f1 { animation: drift1 14s ease-in-out infinite; }
.f2 { animation: drift2 16s ease-in-out infinite; }
.f3 { animation: drift3 15s ease-in-out infinite; }
.f4 { animation: drift4 17s ease-in-out infinite; }
.f5 { animation: drift5 13s ease-in-out infinite; }
.f6 { animation: drift6 18s ease-in-out infinite; }

@keyframes drift1{ 0%,100%{transform: translate(0,0)} 50%{transform: translate(12px,-14px)} }
@keyframes drift2{ 0%,100%{transform: translate(0,0)} 50%{transform: translate(-14px,-10px)} }
@keyframes drift3{ 0%,100%{transform: translate(0,0)} 50%{transform: translate(10px,12px)} }
@keyframes drift4{ 0%,100%{transform: translate(0,0)} 50%{transform: translate(-12px,14px)} }
@keyframes drift5{ 0%,100%{transform: translate(0,0)} 50%{transform: translate(8px,-10px)} }
@keyframes drift6{ 0%,100%{transform: translate(0,0)} 50%{transform: translate(-8px,10px)} }

/* ========================= */
/* ОСНОВНОЙ КОНТЕЙНЕР */
/* ========================= */
.wrap {
  position: relative;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 24px;
  z-index: 10;
}

/* ========================= */
/* КАРТОЧКА МЕНЮ */
/* ========================= */
.card {
  width: min(520px, 100%);
  padding: 22px;
  border-radius: 24px;
  background: rgba(255, 255, 255, .10);
  border: 1px solid rgba(255, 255, 255, .12);
  backdrop-filter: blur(12px) saturate(118%);
  -webkit-backdrop-filter: blur(12px) saturate(118%);
  box-shadow: 0 18px 42px rgba(0,0,0,.28);
}

/* ========================= */
/* КНОПКИ */
/* ========================= */
.btn {
  display: block;
  width: 100%;
  text-align: center;
  padding: 17px 16px;
  border-radius: 20px;
  font-size: 19px;
  font-weight: 800;
  color: var(--text);
  text-decoration: none;
  background:
    linear-gradient(
      180deg,
      color-mix(in srgb, var(--accent1) 18%, white 8%) 0%,
      rgba(255,255,255,.08) 100%
    );
  border: 1px solid color-mix(in srgb, var(--accent1) 24%, rgba(255,255,255,.12));
  backdrop-filter: blur(12px) saturate(115%);
  -webkit-backdrop-filter: blur(12px) saturate(115%);
  box-shadow:
    0 10px 22px rgba(0,0,0,.14),
    0 0 14px color-mix(in srgb, var(--accent1) 16%, transparent);
  margin-bottom: 14px;
  transition: all 0.2s ease;
}

/* Светлая тема - серая обводка кнопок */
:root[data-theme="light"] .btn {
  border: 1.5px solid var(--btn-border);
  background: rgba(255, 255, 255, 0.9);
  color: var(--text);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

.btn:active {
  transform: scale(.995);
  box-shadow:
    0 12px 24px rgba(0,0,0,.18),
    0 0 18px color-mix(in srgb, var(--accent1) 20%, transparent);
}

.btn:hover {
  border-color: color-mix(in srgb, var(--accent1) 35%, rgba(255,255,255,.18));
  background:
    linear-gradient(
      180deg,
      color-mix(in srgb, var(--accent1) 22%, white 10%) 0%,
      rgba(255,255,255,.10) 100%
    );
}

/* Светлая тема - hover для кнопок */
:root[data-theme="light"] .btn:hover {
  border-color: var(--accent1);
}

.sub {
  margin-top: 22px;
  text-align: center;
  color: rgba(247, 251, 255, .68);
  font-size: 14px;
}

.ver {
  margin-top: 10px;
  text-align: center;
  font-size: 12px;
  opacity: .50;
}

.langBlock {
  margin-top: 22px;
  border-top: 1px solid rgba(255, 255, 255, .10);
  padding-top: 16px;
}

.langTitle {
  font-size: 13px;
  color: rgba(247, 251, 255, .68);
  margin-bottom: 12px;
  text-align: center;
}

.langPill {
  width: 100%;
  border-radius: 16px;
  padding: 14px 14px;
  background: rgba(255, 255, 255, .10);
  border: 1px solid rgba(255, 255, 255, .12);
  color: var(--text);
  outline: none;
  backdrop-filter: blur(12px) saturate(115%);
  -webkit-backdrop-filter: blur(12px) saturate(115%);
  box-shadow: 0 8px 18px rgba(0,0,0,.12);
  font-size: 15px;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  cursor: pointer;
  transition: all 0.2s ease;
}

/* Светлая тема - серая обводка для кнопки языка */
:root[data-theme="light"] .langPill {
  border: 1.5px solid var(--btn-border);
  background: rgba(255, 255, 255, 0.9);
  color: var(--text);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

.langPill:hover {
  background: rgba(255, 255, 255, .13);
  border-color: color-mix(in srgb, var(--accent1) 26%, rgba(255,255,255,.18));
}

.langPill:active {
  transform: scale(.995);
}

.chev {
  opacity: .8;
}

.themePill {
  position: fixed;
  top: calc(10px + env(safe-area-inset-top));
  left: 10px;
  z-index: 10000;
  padding: 10px 14px;
  border-radius: 18px;
  background:
    linear-gradient(
      180deg,
      color-mix(in srgb, var(--accent1) 16%, white 8%) 0%,
      rgba(255,255,255,.08) 100%
    );
  border: 1px solid color-mix(in srgb, var(--accent1) 24%, rgba(255,255,255,.12));
  color: var(--text);
  backdrop-filter: blur(12px) saturate(115%);
  -webkit-backdrop-filter: blur(12px) saturate(115%);
  font-size: 13px;
  font-weight: 800;
  display: flex;
  align-items: center;
  gap: 10px;
  box-shadow:
    0 8px 18px rgba(0,0,0,.12),
    0 0 12px color-mix(in srgb, var(--accent1) 14%, transparent);
  cursor: pointer;
  transition: all 0.2s ease;
}

/* Светлая тема - серая обводка для кнопки темы */
:root[data-theme="light"] .themePill {
  border: 1.5px solid var(--btn-border);
  background: rgba(255, 255, 255, 0.9);
  color: var(--text);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

.themePill:hover {
  background:
    linear-gradient(
      180deg,
      color-mix(in srgb, var(--accent1) 20%, white 10%) 0%,
      rgba(255,255,255,.11) 100%
    );
  border-color: color-mix(in srgb, var(--accent1) 30%, rgba(255,255,255,.18));
}

.themePill:active {
  transform: scale(.985);
}

/* ========================= */
/* BOTTOM SHEETS - ВОЗВРАЩАЕМ КАК БЫЛО */
/* ========================= */
.langOverlay, .themeOverlay {
  position: fixed;
  inset: 0;
  z-index: 9999;
  background: rgba(0,0,0,.34);
  display: none;
}

.langOverlay.show, .themeOverlay.show {
  display: block;
}

.langSheet, .themeSheet {
  position: absolute;
  left: 12px;
  right: 12px;
  bottom: calc(12px + env(safe-area-inset-bottom));
  border-radius: 18px;
  background: rgba(24, 31, 40, .97);
  border: 1px solid rgba(255, 255, 255, .10);
  backdrop-filter: blur(16px) saturate(118%);
  -webkit-backdrop-filter: blur(16px) saturate(118%);
  box-shadow: 0 20px 44px rgba(0,0,0,.32);
  overflow: hidden;
  transform: translateY(110%);
  opacity: 0;
  transition: transform .35s cubic-bezier(.2,.8,.2,1), opacity .25s ease;
}

/* Светлая тема - возвращаем как было для bottom sheets */
:root[data-theme="light"] .langSheet,
:root[data-theme="light"] .themeSheet {
  background: rgba(24, 31, 40, .97);
  border: 1px solid rgba(255, 255, 255, .10);
}

.langOverlay.show .langSheet,
.themeOverlay.show .themeSheet {
  transform: translateY(0);
  opacity: 1;
}

.langSheetHeader, .themeSheetHeader {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px;
  border-bottom: 1px solid rgba(255, 255, 255, .09);
}

.langSheetTitle, .themeSheetTitle {
  font-weight: 800;
  color: var(--text);
}

.langClose, .themeClose {
  border: 0;
  background: rgba(255, 255, 255, .08);
  color: var(--text);
  border: 1px solid rgba(255, 255, 255, .10);
  border-radius: 12px;
  padding: 8px 10px;
  font-weight: 800;
  cursor: pointer;
  transition: all 0.2s ease;
}

.langClose:hover, .themeClose:hover {
  background: rgba(255, 255, 255, .11);
  border-color: rgba(255, 255, 255, .16);
}

.langList, .themeList {
  height: 40vh;
  overflow-y: auto;
  -webkit-overflow-scrolling: touch;
}

.langItem, .themeItem {
  width: 100%;
  text-align: left;
  padding: 14px;
  border: 0;
  border-bottom: 1px solid rgba(255, 255, 255, .07);
  background: transparent;
  color: var(--text);
  font-size: 15px;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: space-between;
  cursor: pointer;
  transition: all 0.2s ease;
}

.langItem:hover, .themeItem:hover {
  background: rgba(255, 255, 255, .06);
  border-bottom: 1px solid rgba(255, 255, 255, .10);
}

.langItem .check, .themeItem .check {
  opacity: 0;
  transform: scale(.9);
  transition: .15s ease;
  color: var(--accent1);
}

.langItem.selected .check,
.themeItem.selected .check {
  opacity: 1;
  transform: scale(1);
}

.toast-notification {
  position: fixed;
  top: 20px;
  left: 50%;
  transform: translateX(-50%);
  background: rgba(24, 31, 40, .97);
  border: 1px solid rgba(255, 255, 255, .10);
  border-radius: 24px;
  padding: 12px 20px;
  color: var(--text);
  font-weight: 600;
  backdrop-filter: blur(14px);
  -webkit-backdrop-filter: blur(14px);
  box-shadow: 0 10px 24px rgba(0,0,0,0.26);
  z-index: 100000;
  animation: slideDown 0.3s ease, fadeOut 0.3s ease 2.7s forwards;
  pointer-events: none;
  white-space: nowrap;
}

@keyframes slideDown {
  from {
    transform: translate(-50%, -100%);
    opacity: 0;
  }
  to {
    transform: translate(-50%, 0);
    opacity: 1;
  }
}

@keyframes fadeOut {
  to {
    opacity: 0;
    transform: translate(-50%, -12px);
  }
}