# Contributing / المساهمة

Thank you for improving Bulk Renamer Pro. Keep changes focused, safe, and testable.

1. Create a branch from `main`.
2. Install with `python -m pip install -e . pytest ruff`.
3. Add tests for behavior changes, especially filesystem safety cases.
4. Run `ruff check src tests` and `pytest -q`.
5. Open a pull request describing the user-visible behavior and safety impact.

Do not commit real personal files, credentials, tokens, generated environments, or destructive defaults. Any filesystem mutation must remain preview-first or otherwise require explicit user intent.

## العربية

نرحب بالمساهمات المركزة والقابلة للاختبار. أضف اختبارات لأي تغيير في السلوك، خصوصًا حالات سلامة الملفات، وشغّل `ruff` و`pytest` قبل فتح Pull Request. لا تضف بيانات شخصية أو أسرارًا أو إعدادات حذف/استبدال خطرة افتراضيًا.

Maintainer: **Radwan Abdulhadi Ahmed / رضوان عبدالهادي أحمد — @rad03i2**
