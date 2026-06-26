# CHANGELOG - Factory Mapping / Customer 改名 Factory

版本日期：2026-06-25

## 修改目的

原報表在 `Monthly_Loading`、`Weekly_Loading`、`Date_Loading`、`Risk_List`、`已出貨_Shipped` 中使用 `customer` 欄位，但使用者實際需要顯示工廠名稱 `Factory`。因原始 backlog Excel 不含工廠名稱，因此新增外部 Factory 對照表。

## 修改內容

### 1. 新增 Factory 對照表讀取

新增檔案：

```text
core/factory_mapping.py
```

支援格式：

```text
.xlsx / .xlsm / .xls / .csv
```

對照表必要欄位：

```text
region
model_keyword
Factory
```

比對邏輯：

```text
region 相同 或 region=ALL
且 model_keyword 包含於 model_normalized / model_raw
→ 填入 Factory
```

若找不到對照：

```text
Factory = Unknown
factory_mapping_status = MISSING
```

### 2. GUI 新增上傳欄位

修改檔案：

```text
app.py
```

新增：

```text
上傳 Factory 對照表（factory_mapping.xlsx / csv，可選）
```

### 3. 報表欄位改名

修改檔案：

```text
reports/dvt_report_writer.py
core/loading_matrix.py
```

以下 Sheet 將使用 `Factory` 欄位：

```text
Monthly_Loading
Weekly_Loading
Date_Loading
Risk_List
已出貨_Shipped
```

### 4. Check_Log 查核

新增查核欄位：

```text
factory_mapping_missing_rows
factory_mapping_matched_rows
```

### 5. 新增對照表範本

新增：

```text
config/factory_mapping_template_20260625.xlsx
config/factory_mapping_template.csv
```

## 查核與驗證

已執行：

```text
python -m py_compile app.py main.py core/factory_mapping.py core/loading_matrix.py reports/dvt_report_writer.py
```

已執行 CLI 測試：

```text
python main.py input.zip --as-of-date 2026-06-25 --factory-mapping test_factory_mapping.csv
```

驗證結果：

```text
PASS - 程式可成功產生報表
PASS - Monthly_Loading / Weekly_Loading / Date_Loading 欄位出現 Factory
PASS - 已出貨_Shipped 欄位出現 Factory
PASS - Check_Log 出現 factory_mapping_missing_rows / factory_mapping_matched_rows
PASS - 找不到對照時顯示 Unknown
```

## 使用注意

若報表出現 `Unknown`，請更新 `factory_mapping.xlsx` 的 `model_keyword` 與 `Factory`。

