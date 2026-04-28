/* ============================================================
   Carvix — i18n (RU / EN).
   Использование:
     1. Подключите <script src="/i18n.js"></script> ДО любого app-кода.
     2. Для статичных строк HTML  — атрибут data-i18n="key".
        Поддерживается также data-i18n-placeholder, data-i18n-title.
     3. Для динамических строк JS — функция t('key', vars?).
     4. Сменить язык: setLang('en') | setLang('ru').
   Текущий язык хранится в localStorage.carvix_lang.
   ============================================================ */
(function () {
  const DICT = {
    ru: {
      // ---- Общее ----
      'common.logout':         'Выйти',
      'common.add':            'Добавить',
      'common.cancel':         'Отмена',
      'common.save':           'Сохранить',
      'common.apply':          'Применить',
      'common.reset':          'Сбросить',
      'common.delete':         'Удалить',
      'common.confirm_delete': 'Удалить эту запись?',
      'common.loading':        'Загрузка…',
      'common.no_data':        'Нет данных',
      'common.all':            'Все',
      'common.theme':          'Тема',
      'common.language':       'Язык',

      // ---- Auth (страница входа) ----
      'auth.tab_login':        'Вход',
      'auth.tab_register':     'Регистрация',
      'auth.login':            'Логин',
      'auth.password':         'Пароль',
      'auth.fio':              'ФИО',
      'auth.signin':           'Войти',
      'auth.signup':           'Создать аккаунт',
      'auth.no_account':       'Нет аккаунта?',
      'auth.have_account':     'Уже есть аккаунт?',
      'auth.title':            'Добро пожаловать в Carvix',
      'auth.subtitle':         'Управление автопарком и финансами в одной системе',
      'auth.feat_1':           'Учёт ремонтов и запчастей',
      'auth.feat_2':           'Финансовый модуль с TCO и бюджетами',
      'auth.feat_3':           'Гибкая ролевая модель доступа',

      // ---- Sidebar nav ----
      'nav.dashboard':         'Дашборд',
      'nav.expenses':          'Расходы',
      'nav.budgets':           'Бюджеты',
      'nav.tco':               'Парк (TCO)',
      'nav.receipts':          'Приходы',
      'nav.audit':             'Журнал',

      // ---- Dashboard ----
      'dashboard.title':       'Дашборд',
      'dashboard.subtitle':    'Финансовый обзор за {year} год',
      'dashboard.kpi_month':   'Расходы за месяц',
      'dashboard.kpi_plan':    'План на год',
      'dashboard.kpi_dev':     'Отклонение от плана',
      'dashboard.kpi_top':     'Машин в топ-5',
      'dashboard.fact':        'факт',
      'dashboard.over':        'перерасход',
      'dashboard.left':        'остаток',
      'dashboard.tco_top_hint': 'по стоимости владения',
      'dashboard.dynamics':    'Динамика расходов помесячно',
      'dashboard.structure':   'Структура затрат',
      'dashboard.top5':        'Топ-5 машин по стоимости владения (TCO)',
      'dashboard.delta_up':    '▲ +{n}% к предыдущему',
      'dashboard.delta_down':  '▼ {n}% к предыдущему',

      // ---- Expenses ----
      'expenses.title':        'Расходы',
      'expenses.subtitle':     'Объединённая лента всех затрат',
      'expenses.add':          '+ Добавить расход',
      'expenses.col_date':     'Дата',
      'expenses.col_cat':      'Категория',
      'expenses.col_plate':    'Гос. №',
      'expenses.col_division': 'Подразделение',
      'expenses.col_desc':     'Описание',
      'expenses.col_sum':      'Сумма',
      'expenses.empty':        'Расходы не найдены',
      'expenses.total':        'Всего записей: {n}',
      'expenses.sum_total':    'Сумма: {sum}',
      'expenses.modal_title':  'Добавить расход',
      'expenses.no_division':  '— не указано —',

      // ---- Budgets ----
      'budgets.title':         'Бюджеты — план / факт',
      'budgets.subtitle':      'Сравнение плановых и фактических расходов',
      'budgets.kpi_plan':      'План',
      'budgets.kpi_fakt':      'Факт',
      'budgets.kpi_dev':       'Отклонение',
      'budgets.kpi_pct':       '% исполнения',
      'budgets.col_division':  'Подразделение',
      'budgets.col_period':    'Период',
      'budgets.col_cat':       'Категория',
      'budgets.col_plan':      'План',
      'budgets.col_fakt':      'Факт',
      'budgets.col_dev':       'Отклонение',
      'budgets.col_pct':       '% исп.',
      'budgets.empty':         'Бюджеты не найдены',

      // ---- TCO ----
      'tco.title':             'Парк — TCO',
      'tco.subtitle':          'Стоимость владения по каждому транспортному средству',
      'tco.col_plate':         'Гос. №',
      'tco.col_model':         'Марка / модель',
      'tco.col_division':      'Подразделение',
      'tco.col_repairs':       'Ремонтов',
      'tco.col_works':         'Работы',
      'tco.col_parts':         'Запчасти',
      'tco.col_other':         'Прочее',
      'tco.col_tco':           'TCO итого',
      'tco.sort_tco_desc':     'TCO по убыванию',
      'tco.sort_tco_asc':      'TCO по возрастанию',
      'tco.sort_repairs':      'Кол-во ремонтов',
      'tco.sort_plate':        'Гос. номер',
      'tco.cars_count':        'Машин: {n}',
      'tco.tco_total':         'Итого TCO: {sum}',
      'tco.detail_division':   'Подразделение',
      'tco.detail_orders':     'Заявок / ремонтов',
      'tco.detail_total':      'TCO итого',
      'tco.detail_breakdown':  'В т.ч. работы / запчасти / прочее',
      'tco.history':           'История ремонтов',
      'tco.history_type':      'Тип',
      'tco.history_start':     'Начало',
      'tco.history_end':       'Окончание',
      'tco.history_mech':      'Механик',
      'tco.history_total':     'Итого',
      'tco.history_empty':     'Ремонтов нет',

      // ---- Receipts ----
      'receipts.title':        'Приходные накладные',
      'receipts.subtitle':     'Закупки запчастей у поставщиков',
      'receipts.col_date':     'Дата',
      'receipts.col_num':      '№ накладной',
      'receipts.col_supplier': 'Поставщик',
      'receipts.col_creator':  'Создал',
      'receipts.col_pos':      'Позиций',
      'receipts.col_units':    'Единиц',
      'receipts.col_sum':      'Сумма',
      'receipts.empty':        'Накладных нет',
      'receipts.detail_title': 'Накладная № {n}',
      'receipts.detail_sup':   'Поставщик',
      'receipts.detail_date':  'Дата',
      'receipts.detail_creator': 'Создал',
      'receipts.detail_sum':   'Сумма',
      'receipts.pos_part':     'Запчасть',
      'receipts.pos_sku':      'Артикул',
      'receipts.pos_qty':      'Кол-во',
      'receipts.pos_price':    'Цена',
      'receipts.pos_total':    'Итого',

      // ---- Audit ----
      'audit.title':           'Журнал операций',
      'audit.subtitle':        'Все финансовые действия пользователей',
      'audit.col_when':        'Дата / время',
      'audit.col_user':        'Сотрудник',
      'audit.col_role':        'Роль',
      'audit.col_op':          'Операция',
      'audit.col_obj':         'Объект',
      'audit.col_sum':         'Сумма',
      'audit.col_comment':     'Комментарий',
      'audit.empty':           'Журнал пуст',
      'audit.records':         'Записей: {n}',

      // ---- Filters ----
      'filter.from':           'С даты',
      'filter.to':             'По дату',
      'filter.category':       'Категория',
      'filter.source':         'Источник',
      'filter.year':           'Год',
      'filter.month':          'Месяц',
      'filter.sort':           'Сортировка',
      'filter.src_all':        'Все',
      'filter.src_misc':       'Прочие',
      'filter.src_works':      'Работы',
      'filter.src_repair_parts': 'Запчасти ремонтов',

      // ---- Categories ----
      'cat.remont':            'Ремонт',
      'cat.zapchasti':         'Запчасти',
      'cat.topliv':            'Топливо',
      'cat.strakhovka':        'Страховка',
      'cat.nalog':             'Налог',
      'cat.moyka':             'Мойка',
      'cat.prochee':           'Прочее',

      // ---- Toasts ----
      'toast.deleted':         'Удалено',
      'toast.saved':           'Сохранено',
      'toast.expense_added':   'Расход добавлен',
      'toast.fill_required':   'Заполните дату и сумму',
      'toast.no_rights':       'Недостаточно прав для этого раздела',
      'toast.auth_error':      'Ошибка авторизации',
    },

    en: {
      // ---- Common ----
      'common.logout':         'Sign out',
      'common.add':            'Add',
      'common.cancel':         'Cancel',
      'common.save':           'Save',
      'common.apply':          'Apply',
      'common.reset':          'Reset',
      'common.delete':         'Delete',
      'common.confirm_delete': 'Delete this record?',
      'common.loading':        'Loading…',
      'common.no_data':        'No data',
      'common.all':            'All',
      'common.theme':          'Theme',
      'common.language':       'Language',

      // ---- Auth ----
      'auth.tab_login':        'Sign in',
      'auth.tab_register':     'Register',
      'auth.login':            'Username',
      'auth.password':         'Password',
      'auth.fio':              'Full name',
      'auth.signin':           'Sign in',
      'auth.signup':           'Create account',
      'auth.no_account':       'No account?',
      'auth.have_account':     'Have an account?',
      'auth.title':            'Welcome to Carvix',
      'auth.subtitle':         'Fleet management and finance in one system',
      'auth.feat_1':           'Repair & parts tracking',
      'auth.feat_2':           'Financial module with TCO and budgets',
      'auth.feat_3':           'Flexible role-based access',

      // ---- Sidebar nav ----
      'nav.dashboard':         'Dashboard',
      'nav.expenses':          'Expenses',
      'nav.budgets':           'Budgets',
      'nav.tco':               'Fleet (TCO)',
      'nav.receipts':          'Receipts',
      'nav.audit':             'Audit log',

      // ---- Dashboard ----
      'dashboard.title':       'Dashboard',
      'dashboard.subtitle':    'Financial overview for {year}',
      'dashboard.kpi_month':   'Monthly expenses',
      'dashboard.kpi_plan':    'Annual plan',
      'dashboard.kpi_dev':     'Plan deviation',
      'dashboard.kpi_top':     'Cars in top-5',
      'dashboard.fact':        'actual',
      'dashboard.over':        'overrun',
      'dashboard.left':        'remaining',
      'dashboard.tco_top_hint': 'by total cost of ownership',
      'dashboard.dynamics':    'Monthly expenses dynamics',
      'dashboard.structure':   'Cost structure',
      'dashboard.top5':        'Top-5 vehicles by TCO',
      'dashboard.delta_up':    '▲ +{n}% vs previous',
      'dashboard.delta_down':  '▼ {n}% vs previous',

      // ---- Expenses ----
      'expenses.title':        'Expenses',
      'expenses.subtitle':     'Unified feed of all spendings',
      'expenses.add':          '+ Add expense',
      'expenses.col_date':     'Date',
      'expenses.col_cat':      'Category',
      'expenses.col_plate':    'Plate №',
      'expenses.col_division': 'Division',
      'expenses.col_desc':     'Description',
      'expenses.col_sum':      'Amount',
      'expenses.empty':        'No expenses found',
      'expenses.total':        'Records: {n}',
      'expenses.sum_total':    'Total: {sum}',
      'expenses.modal_title':  'Add expense',
      'expenses.no_division':  '— not set —',

      // ---- Budgets ----
      'budgets.title':         'Budgets — plan / actual',
      'budgets.subtitle':      'Plan vs actual comparison',
      'budgets.kpi_plan':      'Plan',
      'budgets.kpi_fakt':      'Actual',
      'budgets.kpi_dev':       'Deviation',
      'budgets.kpi_pct':       '% of plan',
      'budgets.col_division':  'Division',
      'budgets.col_period':    'Period',
      'budgets.col_cat':       'Category',
      'budgets.col_plan':      'Plan',
      'budgets.col_fakt':      'Actual',
      'budgets.col_dev':       'Deviation',
      'budgets.col_pct':       '% used',
      'budgets.empty':         'No budgets found',

      // ---- TCO ----
      'tco.title':             'Fleet — TCO',
      'tco.subtitle':          'Total cost of ownership per vehicle',
      'tco.col_plate':         'Plate №',
      'tco.col_model':         'Make / model',
      'tco.col_division':      'Division',
      'tco.col_repairs':       'Repairs',
      'tco.col_works':         'Labor',
      'tco.col_parts':         'Parts',
      'tco.col_other':         'Other',
      'tco.col_tco':           'TCO total',
      'tco.sort_tco_desc':     'TCO descending',
      'tco.sort_tco_asc':      'TCO ascending',
      'tco.sort_repairs':      'Repair count',
      'tco.sort_plate':        'Plate number',
      'tco.cars_count':        'Cars: {n}',
      'tco.tco_total':         'Total TCO: {sum}',
      'tco.detail_division':   'Division',
      'tco.detail_orders':     'Orders / repairs',
      'tco.detail_total':      'TCO total',
      'tco.detail_breakdown':  'Of which labor / parts / other',
      'tco.history':           'Repair history',
      'tco.history_type':      'Type',
      'tco.history_start':     'Start',
      'tco.history_end':       'End',
      'tco.history_mech':      'Mechanic',
      'tco.history_total':     'Total',
      'tco.history_empty':     'No repairs',

      // ---- Receipts ----
      'receipts.title':        'Goods receipts',
      'receipts.subtitle':     'Parts purchases from suppliers',
      'receipts.col_date':     'Date',
      'receipts.col_num':      'Receipt №',
      'receipts.col_supplier': 'Supplier',
      'receipts.col_creator':  'Created by',
      'receipts.col_pos':      'Items',
      'receipts.col_units':    'Units',
      'receipts.col_sum':      'Total',
      'receipts.empty':        'No receipts',
      'receipts.detail_title': 'Receipt № {n}',
      'receipts.detail_sup':   'Supplier',
      'receipts.detail_date':  'Date',
      'receipts.detail_creator': 'Created by',
      'receipts.detail_sum':   'Total',
      'receipts.pos_part':     'Part',
      'receipts.pos_sku':      'SKU',
      'receipts.pos_qty':      'Qty',
      'receipts.pos_price':    'Price',
      'receipts.pos_total':    'Total',

      // ---- Audit ----
      'audit.title':           'Audit log',
      'audit.subtitle':        'All financial user actions',
      'audit.col_when':        'When',
      'audit.col_user':        'User',
      'audit.col_role':        'Role',
      'audit.col_op':          'Operation',
      'audit.col_obj':         'Object',
      'audit.col_sum':         'Amount',
      'audit.col_comment':     'Comment',
      'audit.empty':           'Log is empty',
      'audit.records':         'Records: {n}',

      // ---- Filters ----
      'filter.from':           'From',
      'filter.to':             'To',
      'filter.category':       'Category',
      'filter.source':         'Source',
      'filter.year':           'Year',
      'filter.month':          'Month',
      'filter.sort':           'Sort by',
      'filter.src_all':        'All',
      'filter.src_misc':       'Misc',
      'filter.src_works':      'Labor',
      'filter.src_repair_parts': 'Repair parts',

      // ---- Categories ----
      'cat.remont':            'Repair',
      'cat.zapchasti':         'Parts',
      'cat.topliv':            'Fuel',
      'cat.strakhovka':        'Insurance',
      'cat.nalog':             'Tax',
      'cat.moyka':             'Wash',
      'cat.prochee':           'Other',

      // ---- Toasts ----
      'toast.deleted':         'Deleted',
      'toast.saved':           'Saved',
      'toast.expense_added':   'Expense added',
      'toast.fill_required':   'Fill date and amount',
      'toast.no_rights':       'You don\'t have access to this section',
      'toast.auth_error':      'Authorization error',
    },
  };

  /** Текущий язык: localStorage → <html lang> → 'ru'. */
  function getLang() {
    return localStorage.getItem('carvix_lang')
        || document.documentElement.lang
        || 'ru';
  }

  /**
   * Перевести ключ. Поддерживает простую {var} интерполяцию.
   * Если ключ не найден — возвращает сам ключ (helps debugging).
   */
  function t(key, vars) {
    const lang = getLang();
    const dict = DICT[lang] || DICT.ru;
    let raw = dict[key];
    if (raw == null) {
      // fallback на русский
      raw = DICT.ru[key];
      if (raw == null) return key;
    }
    if (vars) {
      raw = raw.replace(/\{(\w+)\}/g, (_, k) => (vars[k] ?? `{${k}}`));
    }
    return raw;
  }

  /** Применить переводы ко всем элементам с data-i18n*. */
  function applyI18n(root = document) {
    root.querySelectorAll('[data-i18n]').forEach(el => {
      el.textContent = t(el.dataset.i18n);
    });
    root.querySelectorAll('[data-i18n-placeholder]').forEach(el => {
      el.placeholder = t(el.dataset.i18nPlaceholder);
    });
    root.querySelectorAll('[data-i18n-title]').forEach(el => {
      el.title = t(el.dataset.i18nTitle);
    });
  }

  /** Сменить язык и переаплаить. Триггерит событие 'langchange'. */
  function setLang(lang) {
    if (!DICT[lang]) lang = 'ru';
    localStorage.setItem('carvix_lang', lang);
    document.documentElement.lang = lang;
    applyI18n();
    document.dispatchEvent(new CustomEvent('langchange', { detail: { lang } }));
  }

  // Применяем сразу при загрузке HTML.
  document.documentElement.lang = getLang();
  document.addEventListener('DOMContentLoaded', () => applyI18n());

  // Экспорт.
  window.t = t;
  window.applyI18n = applyI18n;
  window.setLang = setLang;
  window.getLang = getLang;
})();
