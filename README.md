# Bulk Renamer Pro

**Safe, preview-first batch file renaming for Python 3.10+.**

Bulk Renamer Pro is a local CLI and Python library for predictable bulk renaming without gambling with your files. It builds a complete plan first, fingerprints every source with SHA-256, detects collisions, and changes nothing until `--apply` is explicitly supplied. Every successful run can write a manifest that supports integrity-checked undo.

## Why it exists

Bulk renaming is deceptively risky: destination names can collide, files can change after a preview, and direct A→B renames can fail during swaps. Bulk Renamer Pro treats renaming as a planned operation rather than a sequence of blind filesystem commands.

## Features

- Preview by default; mutation requires `--apply`.
- Natural filename ordering (`photo2` before `photo10`).
- Configurable prefix, suffix, start number, zero-padding, and extension replacement.
- Recursive scanning is opt-in.
- Hidden files are excluded by default; symbolic links are never followed.
- SHA-256 source fingerprints are revalidated immediately before execution.
- Collision detection before mutation.
- Two-phase temporary rename to safely handle rename cycles.
- Best-effort transactional rollback if execution fails mid-run.
- JSON manifest for every applied plan and integrity-checked `undo`.
- Machine-readable JSON preview.
- Zero runtime dependencies; cross-platform Python.

## Install

```bash
git clone https://github.com/rad03i2/bulk-renamer-pro.git
cd bulk-renamer-pro
python -m pip install -e .
```

Requires Python 3.10 or newer.

## Usage

Preview a folder (no files are changed):

```bash
bulk-renamer rename ./photos --prefix "Trip-" --start 1 --width 4
```

Apply the exact kind of plan after reviewing it:

```bash
bulk-renamer rename ./photos --prefix "Trip-" --width 4 --apply --manifest ./rename-manifest.json
```

Add a suffix and replace extensions:

```bash
bulk-renamer rename ./exports --prefix "report-" --suffix "-final" --extension pdf
```

Recursive preview and JSON output:

```bash
bulk-renamer rename ./assets --recursive --prefix "asset-" --json
```

Undo a completed run:

```bash
bulk-renamer undo ./rename-manifest.json
```

Undo refuses to move a renamed file if its SHA-256 no longer matches the manifest or if the original path is occupied.

## Python API

```python
from pathlib import Path
from bulk_renamer import apply, plan, undo

ops = plan(Path("photos"), prefix="Trip-", width=4)
for op in ops:
    print(op.source, "->", op.target)

apply(ops, Path("rename-manifest.json"))
undo(Path("rename-manifest.json"))
```

## Project structure

```text
src/bulk_renamer/   core engine + CLI
tests/              safety and end-to-end tests
.github/workflows/  cross-platform CI
```

## Testing

```bash
python -m pip install -e . pytest ruff
ruff check src tests
pytest -q
```

CI runs on Ubuntu, Windows, and macOS with Python 3.10, 3.12, and 3.13.

## Safety, privacy, and limitations

All processing is local; the application has no networking code and needs no API key. A preview is a snapshot, so execution re-hashes source files before renaming. Symbolic links are skipped. Undo is intentionally conservative and will not overwrite an occupied original path.

The tool renames files, not directories. It does not edit file contents or metadata. Filesystems and external programs can still mutate files concurrently; no userspace utility can make a multi-file rename globally atomic across all filesystems. The rollback is best-effort when the OS itself fails during recovery.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Security concerns should follow [SECURITY.md](SECURITY.md).

## License

MIT — see [LICENSE](LICENSE).

## Author

**Radwan Abdulhadi Ahmed**  
**رضوان عبدالهادي أحمد**  
GitHub: **@rad03i2**

---

# العربية

## Bulk Renamer Pro — إعادة تسمية جماعية آمنة

أداة سطر أوامر ومكتبة Python لإعادة تسمية الملفات جماعيًا بصورة واضحة وآمنة. تبدأ الأداة دائمًا بالمعاينة، وتحسب بصمة SHA-256 لكل ملف، وتتحقق من تعارض الأسماء، ولا تنفذ أي تغيير إلا عند إضافة `--apply` صراحةً. بعد التنفيذ يُحفظ Manifest يمكن استخدامه للتراجع مع التحقق من سلامة الملفات.

## لماذا هذا المشروع؟

إعادة تسمية عدد كبير من الملفات قد تسبب فقدان أسماء أو استبدال ملفات عند وجود تعارضات. لذلك يفصل المشروع بين **التخطيط** و**التنفيذ**، ويعيد التحقق من الملفات قبل أي تعديل، ويستخدم مرحلتين لإعادة التسمية لتجنب تعارضات التبديل بين الأسماء.

## المميزات

- معاينة افتراضية بلا تعديل للملفات.
- ترتيب طبيعي للأسماء والأرقام.
- تخصيص البادئة واللاحقة ورقم البداية وعدد خانات الرقم والامتداد.
- البحث داخل المجلدات الفرعية اختياري.
- تجاهل الملفات المخفية افتراضيًا وعدم اتباع الروابط الرمزية.
- بصمة SHA-256 والتحقق منها قبل التنفيذ والتراجع.
- اكتشاف تعارضات أسماء الوجهة قبل التعديل.
- إعادة تسمية على مرحلتين مع محاولة rollback عند فشل التنفيذ.
- Manifest بصيغة JSON وميزة Undo آمنة.
- إخراج JSON للمعاينة والدمج مع أدوات أخرى.
- لا توجد تبعيات تشغيل خارجية.

## التثبيت

```bash
git clone https://github.com/rad03i2/bulk-renamer-pro.git
cd bulk-renamer-pro
python -m pip install -e .
```

يتطلب Python 3.10 أو أحدث.

## الاستخدام

معاينة فقط:

```bash
bulk-renamer rename ./photos --prefix "Trip-" --width 4
```

التنفيذ بعد مراجعة الخطة:

```bash
bulk-renamer rename ./photos --prefix "Trip-" --width 4 --apply --manifest ./rename-manifest.json
```

التراجع:

```bash
bulk-renamer undo ./rename-manifest.json
```

يمكن استخدام `--recursive` للمجلدات الفرعية و`--json` للحصول على خطة قابلة للمعالجة آليًا و`--extension` لتغيير الامتداد.

## الاختبارات

```bash
python -m pip install -e . pytest ruff
ruff check src tests
pytest -q
```

يختبر GitHub Actions المشروع على Windows وLinux وmacOS وإصدارات Python 3.10 و3.12 و3.13.

## الخصوصية والأمان والقيود

كل العمل محلي ولا يحتوي المشروع على اتصال شبكي أو مفاتيح API. لا يتم اتباع الروابط الرمزية، ولا يُستبدل ملف موجود بصمت، ويرفض Undo العمل إذا تغير محتوى الملف أو أصبح مساره الأصلي مشغولًا. المشروع يعيد تسمية **الملفات فقط** ولا يعدل محتواها أو metadata الخاصة بها. الـrollback محاولة آمنة قدر الإمكان، لكنه لا يستطيع ضمان الذرية الكاملة عبر جميع أنظمة الملفات في حال حدوث فشل على مستوى نظام التشغيل نفسه.

## المساهمة والترخيص

راجع [CONTRIBUTING.md](CONTRIBUTING.md) للمساهمة و[SECURITY.md](SECURITY.md) للإبلاغ الأمني. المشروع مرخص وفق MIT كما هو موضح في [LICENSE](LICENSE).

## المؤلف

**Radwan Abdulhadi Ahmed**  
**رضوان عبدالهادي أحمد**  
GitHub: **@rad03i2**
