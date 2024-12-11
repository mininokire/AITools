REPORT z_export_table_structure_screen.

* 数据声明
DATA: lt_fieldinfo TYPE STANDARD TABLE OF dd03l,  "字段信息
      ls_fieldinfo TYPE dd03l,                   "单个字段信息
      lt_tables    TYPE TABLE OF string,         "表名列表
      lv_line      TYPE string.                 "CSV 行

DATA: lv_path      TYPE string.                 "保存路径
DATA: lv_filename  TYPE string VALUE 'SAP_TABLE_STRUCTURE.csv'. "默认文件名
DATA: lv_fullpath  TYPE string.                 "完整路径

* 选择屏幕参数
PARAMETERS: p_tables TYPE string OBLIGATORY.    "表名输入（逗号分隔）
PARAMETERS: p_path TYPE string LOWER CASE DEFAULT ''. "保存路径

AT SELECTION-SCREEN ON VALUE-REQUEST FOR p_path.
  " 文件路径选择框
  CALL FUNCTION 'F4_FILENAME'
    EXPORTING
      program_name  = sy-repid
      dynpro_number = sy-dynnr
      field_name    = 'P_PATH'
    IMPORTING
      file_name     = p_path.
  IF sy-subrc <> 0.
    WRITE: / '文件路径选择失败，请重试！'.
  ENDIF.

START-OF-SELECTION.
  " 校验输入路径
  IF p_path IS INITIAL.
    WRITE: / '保存路径未指定，请重新运行程序！'.
    STOP.
  ENDIF.

  " 拼接完整路径
  CONCATENATE p_path lv_filename INTO lv_fullpath.

  " 打开文件
  OPEN DATASET lv_fullpath FOR OUTPUT IN TEXT MODE ENCODING DEFAULT.
  IF sy-subrc <> 0.
    WRITE: / '无法打开文件:', lv_fullpath.
    STOP.
  ENDIF.

  " 写入表头行
  lv_line = 'Table Name,Field Name,Data Type,Length,Decimal Places'.
  TRANSFER lv_line TO lv_fullpath.

  " 分割输入的表名
  SPLIT p_tables AT ',' INTO TABLE lt_tables.

  " 遍历表名并写入字段信息
  LOOP AT lt_tables INTO DATA(lv_tablename).
    CLEAR lt_fieldinfo.

    " 获取表的字段信息
    SELECT * FROM dd03l INTO TABLE lt_fieldinfo WHERE tabname = lv_tablename.
    IF sy-subrc <> 0.
      WRITE: / '表', lv_tablename, '不存在或无字段信息.'.
      CONTINUE.
    ENDIF.

    " 写入表字段信息到CSV
    LOOP AT lt_fieldinfo INTO ls_fieldinfo.
      CLEAR lv_line.
      CONCATENATE lv_tablename
                  ls_fieldinfo-fieldname
                  ls_fieldinfo-datatype
                  ls_fieldinfo-leng
                  ls_fieldinfo-decimals
                  INTO lv_line SEPARATED BY ','.
      TRANSFER lv_line TO lv_fullpath.
    ENDLOOP.
  ENDLOOP.

  " 关闭文件
  CLOSE DATASET lv_fullpath.

  " 输出完成消息
  WRITE: / '表结构导出完成，文件保存到：', lv_fullpath.
