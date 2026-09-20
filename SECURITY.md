# Security Policy

Bulk Renamer Pro operates on local files, so data-loss prevention is treated as a security property.

## Supported version

The latest release on `main` is supported.

## Reporting

Please report a suspected vulnerability privately through GitHub's security reporting features when available. Do not include private documents, credentials, or sensitive file contents in a public issue.

Useful reports include reproduction steps, operating system/filesystem details, expected behavior, and the smallest safe example possible.

## Safety guarantees and boundaries

- Preview is the default; execution requires `--apply`.
- Existing unrelated targets are rejected.
- Source SHA-256 values are checked before mutation.
- Undo validates content and refuses occupied original paths.
- Symlinks are skipped.
- Multi-file operations cannot be globally atomic on every filesystem; rollback after an OS/filesystem failure is best-effort.

## العربية

يتعامل المشروع مع ملفات محلية، لذلك تُعد حماية البيانات جزءًا أساسيًا من الأمان. لا ترسل ملفاتك الخاصة أو كلمات المرور أو الأسرار ضمن Issue عام. الأداة تعمل بالمعاينة افتراضيًا، تتحقق من SHA-256 قبل التنفيذ والتراجع، وترفض استبدال المسارات المشغولة. تبقى عملية rollback أفضل محاولة ممكنة وليست ضمانًا للذرية الكاملة عند فشل نظام التشغيل أو نظام الملفات.

Maintainer: **Radwan Abdulhadi Ahmed / رضوان عبدالهادي أحمد — @rad03i2**
