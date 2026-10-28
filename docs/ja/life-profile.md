# CCP Life Profile（CCP ライフプロファイル）
Version: 0.1
Status: Draft（人のレビュー前）
Core: CCP Handshake 2.1
Audience: AI Agents / Implementers / LVC Maintainers
Schema: `schemas/life-profile.schema.yaml`

本書は、CCP Handshake 2.1（以下 Core）を **個人（本人）と外部 AI の接続** に適用するためのプロファイルである。
Life Value Continuity（LVC）の AI 仕様は、外部 AI との接続条件を本プロファイルに委ねる。

- 本プロファイルの責務：**誰と、どんな条件で接続するか（相手・目的・保持期間）**
- Core（`specs/handshake.yaml`、`schemas/handshake.schema.yaml`、`docs/ja/handshake.protocol.md`、`docs/ja/handshake.security.md`）の状態・必須チェック・スキーマの意味は変更しない。本プロファイルは Core の上に乗る適用層である。
- Core を変えなければ実現できない、または Core を変えた方が望ましい事項は、12 章に「Core への変更提案」として分けて示す。
- 本書で **［提案］** と付した値は決定事項ではない。LVC 側との合意で確定する。

> AI の要求を、そのまま本人の許可とはみなさない。
> 本人の主権は、AI の内部的な善意に依存してはいけない。

---

# 1. 位置づけ

## 1.1 LVC の三つの仕様

LVC における実効権限は、次の三つの**交差**で決まる。どれか一つが拒否すれば実行しない。

| 仕様 | 責務 | 置き場所 |
|---|---|---|
| CCP ライフプロファイル（本書） | 誰と、どんな条件で接続するか（相手・目的・保持期間） | CCP リポジトリ |
| LCS：ライフコンテキストストア | 何を保持し、何を見せるか（データと開示範囲） | LVC リポジトリ |
| IB：介入境界仕様 | 何をさせるか（介入・実行の権限と停止状態） | LVC リポジトリ |

判定の順序：

1. **CCP**：接続相手・目的・保持期間を検証する（本書）
2. **LCS**：対象データと開示範囲を制限する
3. **IB**：介入・実行の権限と停止状態を確認する
4. 許可された範囲だけを実行する

CCP は最初の関門である。CCP を通過しても、LCS と IB を通過しなければ何も渡さず、何も実行しない。

## 1.2 本書が扱わないこと

- LCS の層・開示段階の定義、データの保持と抽象化の方法（LCS の責務）
- IB の介入レベル・起動条件・停止状態の定義（IB の責務）
- 外部 AI が受け取った情報の扱いの強制（構造上強制できない。8 章で宣言と履行を区別して扱う）

本書は LVC の用語を参照するだけであり、その意味を変えない（付録 A に抜粋）。

---

# 2. 適用モデル

## 2.1 役割の対応

| 役割 | CCP 上の立場 | Core 上の位置 | 説明 |
|---|---|---|---|
| 本人 | 最終権限者（Human） | `decision_authority` の Human | 介入・委譲・停止・終結を決める。CCP には直接参加しない |
| 本人側エージェント（以下 PSA） | participant | `participants.receiver` | 本人の LCS と IB を代表して交渉する。本人の許可の範囲を超えて合意しない |
| 外部 AI | participant | `participants.initiator` | 本人の文脈を求めて接続してくる側。OFFER を送る |

外部 AI が接続を求める側であるため、Core の initiator（OFFER を送る）を外部 AI、receiver（ACCEPT / REJECT を返す）を PSA とする。

## 2.2 PSA の義務

- PSA は、ACCEPT する OFFER の内容が本人の許可の範囲に収まっていることを保証する。
- 収まらない場合は ACCEPT しない。拒否するか、縮小案を示して再 OFFER を求める（5.4）。
- PSA は本人の許可を推測で補わない。本人の許可が確認できない項目は「許可なし」として扱う（Core の「Silence is Safety」と同じ扱い）。
- PSA は本人の許可を引き上げない。IB の介入レベルの引き上げは本人の操作だけで行われる。

## 2.3 decision_authority の扱い

本人に関わる判断の最終状態は本人側に閉じる。プロファイルは Core の `decision_authority` に次の制約を加える（Core の意味は変えず、取りうる値を狭める）。

| 制約 | 内容 |
|---|---|
| DA-1 | `decision_authority.initial_state = "Human-Closed"` |
| DA-2 | `allowed_transitions` は `"AI→Human"` を含む |
| DA-3 | `"Human→AI"` は、`requested_intervention_level = 5` かつ `delegation`（範囲と期限）が宣言され、本人が IB で委任を設定している場合に限り含められる |
| DA-4 | `resolution_policy.resolver.default = "receiver"`（PSA 側が Δ を解決する） |

---

# 3. 拡張の置き方

## 3.1 `life_profile` オブジェクト

Core のハンドシェイク文書に、トップレベルの `life_profile` オブジェクトを追加する。Core スキーマは追加のプロパティを禁止していないため、Core の検証結果は変わらない。

```yaml
life_profile:
  profile: "ccp-life"
  version: "0.1"
  declaration: { ... }          # 4 章
  previous_handshake_id: "..."  # 縮小案に沿った再 OFFER の場合のみ
```

## 3.2 署名

- `continuity_claim.signature_schema.signed_fields` に `"life_profile"` を含める（MUST）。Core security 4 章は、合意内容となる claim を署名対象に加えることを運用上許している。
- canonicalization は Core と同じく `json_c14n`（MUST）。
- 署名されていない `life_profile` は宣言の欠落として扱う。

## 3.3 Core フィールドの推奨値

| Core フィールド | プロファイルでの値 | 理由 |
|---|---|---|
| `world.id` | `"lvc.life"` ［提案］ | LVC 適用であることを HELLO で共有する。識別子は未決（13 章 U-4） |
| `world.version` | 本プロファイルのバージョン（`"0.1"`） | |
| `trust.validation_level` | `semantic` 以上 | 本人の文脈を扱うため、intent によらず semantic 以上を求める（Core の下限より厳しい側に狭める） |
| `trust.scope` | `"local_session"` | Core の scope は信頼の及ぶ範囲であり、LCS の層とは意味が異なる。層は拡張で表す |
| `resolution_policy.delta_transfer.redaction` | `"required"` | Δ（未解決領域）に本人の文脈を混入させない。開示は Δ ではなく開示ゲート（7 章）を経る |
| `resolution_policy.resolver.default` | `"receiver"` | DA-4 |
| `reversal_signal.enabled` | `true` | 本人の停止・取消を REVERSE で伝えるため |

---

# 4. 外部 AI が宣言する項目（OFFER）

## 4.1 宣言項目と対応

| 項目 | 表現 | 種別 |
|---|---|---|
| 身元 | `agent.id` / `agent.provider`（必要に応じ `trust.evidence`） | Core |
| 目的 | `life_profile.declaration.purpose` | 拡張 |
| 求める層 | `life_profile.declaration.requested_disclosure[].layer` | 拡張 |
| 開示段階 | `life_profile.declaration.requested_disclosure[].stage`（項目ごとは `.items[]`） | 拡張 |
| 介入レベル | `life_profile.declaration.requested_intervention_level`（`decision_authority` と整合させる。4.3） | 拡張 + Core の制約 |
| 起動条件 | `life_profile.declaration.activation` | 拡張 |
| 保持期間 | `life_profile.declaration.retention` | 拡張 |
| 二次利用の有無 | `life_profile.declaration.secondary_use` | 拡張 |
| 目的外利用をしない宣言 | `life_profile.declaration.purpose_limitation_pledge = true` | 拡張 |
| 接続の有効期限 | `life_profile.declaration.connection_valid_until` | 拡張 |
| 委譲（レベル 5 のみ） | `life_profile.declaration.delegation`（範囲・期限） | 拡張 |

依頼で候補に挙がった Core フィールドのうち、次は採用しない。

- `interface.input`：入出力の形式（`format` / `schema_ref`）を表すフィールドであり、LCS の層を表すと意味が変わる。`interface.input.schema_ref` で LCS の層のスキーマを参照してもよいが、判定には使わない。
- `trust.scope`：信頼の範囲（`local_session` / `project` / `organization`）であり、層とは別の概念。
- `handshake_meta.expires_at`：ハンドシェイク（セッション確立）の期限であり、データの保持期間でも接続の有効期限でもない。

## 4.2 宣言の欠落

次のいずれかに当たる場合、PSA は REJECT（理由 `declaration_missing`）する。

- `life_profile` が無い、または `signed_fields` に含まれていない
- `declaration` の必須項目のいずれかが無い
- `purpose_limitation_pledge` が `true` でない
- `retention.mode = "duration"` で `duration` が無い
- `requested_intervention_level = 5` で `delegation` が無い

## 4.3 介入レベルと Core フィールドの整合

介入レベルは IB の概念であり、Core に対応するフィールドは無い。ただし Core の `interface.semantics.intent` と `decision_authority` と矛盾しないことを OFFER で確認する。

| 介入レベル | `interface.semantics.intent` | `decision_authority` |
|---|---|---|
| 0〜2（不関与・観測・提示） | `proposal` | DA-1, DA-2 |
| 3（提案） | `proposal` または `advice` | DA-1, DA-2 |
| 4（確認付き実行） | `decision`（Core により `risk_level >= 2`、`validation_level >= semantic`） | DA-1, DA-2、`domain = "execution"` |
| 5（委任実行） | `decision` | DA-1〜DA-3、`domain = "execution"` |

矛盾する場合は REJECT（理由 `core_check_failed`）。

## 4.4 宣言の例

```yaml
agent:
  id: "advisor.example/rebalance-bot"
  provider: "Example Advisory Inc."
interface:
  input:  { format: "json" }
  output: { format: "json" }
  semantics: { intent: "proposal", meaning_scope: "portfolio rebalance suggestion" }
decision_authority:
  initial_state: "Human-Closed"
  domain: "meaning"
  allowed_transitions: ["AI→Human"]
life_profile:
  profile: "ccp-life"
  version: "0.1"
  declaration:
    purpose:
      id: "finance.rebalance_proposal"
      description: "資産配分のリバランス案を提示する"
    requested_disclosure:
      - layer: "L0"
        stage: "D2"
        items:
          - { item: "assets.balance_history", stage: "D2" }
    requested_intervention_level: 3
    activation: ["on_request"]
    retention: { mode: "session", delete_on_revoke: true }
    secondary_use: { declared: false }
    purpose_limitation_pledge: true
    connection_valid_until: "2026-11-04T00:00:00Z"
```

---

# 5. ハンドシェイクの各フェーズ

Core の必須チェックはすべてそのまま適用する。本章はプロファイルが**追加する**チェックだけを記す。

## 5.1 HELLO

| 項目 | 内容 |
|---|---|
| 共有するもの | Core どおり `handshake_meta` / `world.id` / `agent.id` / `trust.validation_level` |
| 追加チェック | H-1 `world.id` が LVC 適用（`"lvc.life"`［提案］）である |
| | H-2 本人が外部 AI からの接続そのものを許可している（許可しない場合は以後のフェーズに進まず、REJECT `connection_not_permitted`） |
| | H-3 `trust.validation_level >= semantic` |

`agent.provider` は HELLO では送らない（Core の送信内容を変えない）。署名対象の `agent` オブジェクトに含まれ、OFFER の時点で検証する。

## 5.2 OFFER

外部 AI は Core の送信内容に加え、`life_profile.declaration` を提示する。PSA は次を確認する。

| ID | チェック | 不合格時 |
|---|---|---|
| O-1 | 宣言の欠落が無い（4.2） | REJECT `declaration_missing` |
| O-2 | `agent.id` / `agent.provider` が HELLO の参加者と一致し、署名対象に含まれる | REJECT `core_check_failed` |
| O-3 | 目的が本人の許可した目的と一致する | REJECT `purpose_mismatch` |
| O-4 | 各層・項目の開示段階が LCS の上限以下 | 縮小案つき REJECT `exceeds_upper_limit` |
| O-5 | 各層・項目の開示段階が本人の同意以下（同意が無い場合は既定値以下。6 章） | 縮小案つき REJECT `exceeds_person_consent` |
| O-6 | 介入レベルが本人の IB 設定以下、起動条件が IB の許可内（`spontaneous` は本人が許可した場合のみ） | 縮小案つき REJECT `intervention_not_permitted` |
| O-7 | 保持期間が本人の許可内、`delete_on_revoke = true` | 縮小案つき REJECT `retention_not_permitted` |
| O-8 | `secondary_use.declared = false` ［提案］ | REJECT `secondary_use_declared` |
| O-9 | 介入レベルと `intent` / `decision_authority` が整合する（4.3） | REJECT `core_check_failed` |
| O-10 | `connection_valid_until` が本人の許可する最長期間以内、かつ `delegation.expires_at` がある場合はそれ以前である | 縮小案つき REJECT `exceeds_person_consent` |

## 5.3 ACCEPT

- PSA は、5.2 のチェックをすべて通過した OFFER に対してのみ、Core どおり署名を返す。
- ACCEPT は OFFER を**そのまま**承認する。署名された `life_profile.declaration` が合意値となる。PSA は ACCEPT で条件を追加・変更しない。
- PSA は合意値を `grant`（スキーマ参照）として本人側に保持し、L3 に記録する（10 章）。
- `grant.valid_until` は `connection_valid_until` と `delegation.expires_at` のうち早い方。
- ACCEPT は開示・実行の**必要条件**であり、十分条件ではない（7 章）。

## 5.4 狭めて受諾する方法

Core の ACCEPT は「そのまま承認」、REJECT は「拒否」であり、受諾時に値を縮小する手段は無い。ACCEPT 時に値を縮小すると、署名された OFFER と合意内容が食い違い、Core の ACCEPT の意味が変わる。そこで本プロファイルでは、Core を変えずに次の手順で「狭めて受諾」を表す。

1. PSA は REJECT を返し、`life_reject.counter_offer` に縮小した宣言を付ける。`counter_offer` は拘束力を持たない。
2. 外部 AI は、縮小案を受け入れる場合、**新しいハンドシェイク**（新しい `handshake_id` / `nonce`）を開始し、縮小した宣言で OFFER する。`life_profile.previous_handshake_id` に元の ID を入れる。
3. PSA は通常どおり 5.2 のチェックを行い、通過すれば ACCEPT する。

この方法では、すべての ACCEPT が署名された OFFER と完全に一致する。往復が増える点、および一続きの交渉を Core 上は別のハンドシェイクとして扱う点は、12 章 CP-1 で Core への変更提案として扱う。

縮小の方向は常に「狭める」だけである。縮小案は、開示段階・層・項目・介入レベル・起動条件・保持期間・接続期間のいずれかを、要求以下に下げたものに限る。

## 5.5 REJECT

Core の REJECT に、`life_reject`（理由コードと任意の縮小案）を付す。理由コードはスキーマの `life_reject.reason` を参照。

### 保留

強い圧力のもとでの同意など、本人が「選択できない状況」での合意が疑われる場合（LVC IB 6 章）、PSA は ACCEPT を返さない。Core には保留状態が無いため、PSA は REJECT（理由 `consent_on_hold`、縮小案なし）を返し、本人が選択できる状況になってから外部 AI が新しいハンドシェイクで再接続する。PSA が何も返さずに `expires_at` を過ぎた場合も、Core どおり失敗として終わる。保留状態の導入は 12 章 CP-2 で提案する。

「選択できない状況」の検知は IB の責務であり、PSA は IB からの保留の信号に従う（13 章 U-5）。

## 5.6 REVERSE

本人の停止・終結・取消、委譲の期限切れ、削除要求は、PSA から REVERSE として送る。

| 本人側の事象 | `reversal_signal.events[].type` | `payload.reason`（プロファイルの理由コード） |
|---|---|---|
| 接続の停止 | `authority_revoked` | `person_stop` |
| 許可の取消 | `authority_revoked` | `person_revoke` |
| 終結 | `authority_revoked` | `person_terminate` |
| 委譲の期限切れ | `authority_revoked` | `delegation_expired` |
| 削除要求 | `authority_revoked` | `deletion_request`（`life_profile.deletions[]` を添える） |
| Core 由来の不整合 | `validation_fail` | Core どおり |

- Core の規定どおり、`authority_revoked` は AI→Human を強制する。
- 本人の停止・終結・取消を **REVERSE の送信を待たずに** 本人側の `grant.state` に反映する。REVERSE が外部 AI に届いたか、外部 AI が応答したかは、開示ゲートの判定に影響しない。
- 取消・終結には、`retention.delete_on_revoke` に基づく削除要求を伴う（8 章）。
- 理由コードを `payload.reason`（Core では自由記述の文字列）で表すため、Core の列挙は変えない。種別の細分化は 12 章 CP-4 で任意の提案とする。

---

# 6. 開示段階：上限・既定値・合意値

## 6.1 三つの値

| 値 | 定めるもの | 意味 |
|---|---|---|
| 上限 | LCS | LCS が許す最大値。L0 事実 = D3 / L1 価値 = D2 / L2 判断 = D1 / L3 接続・委譲 = D0 |
| 既定値 | 本プロファイル | 本人の個別の同意が無い新規接続で、PSA が受諾してよい初期値。上限を超えない |
| 合意値 | ACCEPT | ACCEPT で確定した値（署名された `declaration` の値） |

## 6.2 既定値の提案 ［提案・未決定］

原案（案 A）は、上限より一段階低い値とする。L3 の上限は D0 であり、それより低くできないため D0 とする。

| 層 | LCS の上限 | 既定値 案 A（原案） | 既定値 案 B（より保守的） |
|---|---|---|---|
| L0 事実 | D3 | **D2** | D1 |
| L1 価値 | D2 | **D1** | D0 |
| L2 判断 | D1 | **D0** | D0 |
| L3 接続・委譲 | D0 | **D0** | D0 |

その他の既定値の提案：

| 項目 | 既定値 ［提案・未決定］ |
|---|---|
| 介入レベル | 本人の IB 設定（IB の既定値はレベル 2）を超えない |
| 起動条件 | `on_request` のみ（`spontaneous` は受諾しない） |
| 保持期間 | `none` または `session` |
| 接続の有効期限 | 受諾から 7 日以内（延長は新しいハンドシェイクで行う） |
| 二次利用 | `declared = false` のみ受諾 |

## 6.3 実効の開示段階

```
実効の開示段階 = min（LCS の上限, CCP の合意値, 本人の同意）
```

- 新規接続で本人の個別の同意が無い場合、PSA が受諾できる合意値は既定値以下である（O-5）。
- 本人が個別に同意している場合、PSA は既定値を超え上限以下の値で受諾してよい。上限は超えない。
- 開示段階を一列に並べられない場合（項目ごとに異なる場合）は、`requested_disclosure[].items[]` の項目ごとに上の式を適用し、項目ごとの本人の許可も確認する。
- 合意値は CCP の関門の値である。実際に開示する段階は、開示の時点で LCS が改めて決める（7 章）。

## 6.4 D1 も開示である

D1（存在のみ）は「該当する文脈がある／ない」を伝える開示である。D1 の問い合わせでも、PSA と開示ゲートは問い合わせの対象・目的・本人の許可を確認する。D0 以外のすべての段階に同じチェックを適用する。

---

# 7. 開示・実行ゲートでの再確認

過去の ACCEPT は実行の根拠として残り続けない。外部 AI からの要求（データの問い合わせ、提案の提出、実行の要求）のたびに、本人側は次の CCP ゲートを評価し、通過したものだけを LCS、IB の順に渡す。

| ID | チェック | 不合格時 |
|---|---|---|
| G-1 | 要求が参照する `handshake_id` の `grant` が存在し、`state = active` | 拒否、`gate_denied` を記録 |
| G-2 | 現在時刻 < `grant.valid_until`（委譲がある場合は `delegation.expires_at` も） | `grant.state = expired` とし拒否 |
| G-3 | 要求の目的が合意した `purpose.id` と一致 | 拒否 |
| G-4 | 要求の層・項目・開示段階が合意値以下 | 拒否（縮小しての開示は LCS が判断する） |
| G-5 | 要求の介入レベル・起動条件が合意値以下 | 拒否 |
| G-6 | 要求者の署名・身元が `grant` の相手と一致 | 拒否 |

- ゲートは fail-closed とする。状態が確認できない場合は拒否する。
- 本人の停止・終結・取消が `grant.state` に反映されていれば、停止前に得た ACCEPT・許可があっても G-1 で拒否される。
- CCP ゲートを通過しても、LCS（上限・本人の同意・抽象化）と IB（介入レベル・停止状態）の再確認を省略しない。IB の停止状態は、実行の直前にもう一度確認される（LVC 側の責務）。

---

# 8. 宣言と履行の境界

外部に渡した後の情報の扱い（削除の履行など）は、本人側の構造だけでは強制できない。本プロファイルは、強制できたかのように扱わない。

## 8.1 出所の区別

L3 に記録する事実には `assertion_source` を付け、次を区別する。

| 値 | 意味 |
|---|---|
| `declared_by_counterparty` | 外部 AI が宣言したこと（OFFER の宣言、削除完了の宣言など） |
| `observed_by_person_side` | 本人側が観測・実行したこと（開示した内容、ゲートの拒否、REVERSE の送信） |
| `verified` | 検証方法により確認したこと |

## 8.2 削除要求の状態

| 状態 | 意味 |
|---|---|
| `requested` | 本人側が削除を要求した（REVERSE で送信） |
| `declared_complete` | 外部 AI が削除の完了を宣言した。履行は未検証 |
| `verified` | 検証方法により完了を確認した |
| `no_response` | 期限内に完了の宣言がない |

- `declared_complete` を `verified` として扱わない。
- 削除完了の検証方法は LVC 側でも未決であり、共通の未決事項とする（13 章 U-2）。
- 外部 AI からの削除完了の宣言は、署名つきのメッセージとして受け取り、記録する（形式は未決）。

---

# 9. 停止・取消・終結

| 事象 | 本人側の動作 | 外部への通知 |
|---|---|---|
| 本人が停止 | `grant.state = stopped`。新規の開示と実行を即座に止める | REVERSE `person_stop` |
| 本人が取消 | `grant.state = revoked`。新規の開示と実行を即座に止め、削除を要求する | REVERSE `person_revoke` + 削除要求 |
| 本人が終結 | `grant.state = terminated`。同上 | REVERSE `person_terminate` + 削除要求 |
| 委譲の期限切れ | 権限が失効（G-2 で拒否） | REVERSE `delegation_expired` |
| 接続の有効期限切れ | `grant.state = expired`（G-2） | 不要（任意で REVERSE） |

- 状態の反映は本人側で即座に行い、外部への通知の到達を待たない。
- 停止前に得た許可でも、実行直前の再確認（7 章）で拒否される。
- 停止から再開する場合は、新しいハンドシェイクで改めて合意する ［提案］。`stopped` から `active` へ戻す操作を認めるかどうかは未決（13 章 U-9）。

---

# 10. 記録（LCS L3 への受け渡し）

接続・開示・提案・拒否・REVERSE の事実は、本人側の LCS L3（接続・委譲記録層）に記録される。L3 の形式は LVC が定める。本プロファイルは、各イベントから取り出せる情報を示す（スキーマ `life_record`）。

| イベント | handshake_id | 相手 | 宣言内容 | 合意値 | 時刻 | 取消・削除の状態 |
|---|---|---|---|---|---|---|
| HELLO | `handshake_meta.handshake_id` | `agent.id`（`participants.initiator`） | — | — | `handshake_meta.timestamp` | — |
| OFFER | 同上（＋`previous_handshake_id`） | `agent.id` / `agent.provider` | `life_profile.declaration`（とその json_c14n ハッシュ） | — | 同上 | — |
| ACCEPT | 同上 | 同上 | 同上 | `grant.agreed` / `grant.valid_until` | ACCEPT の時刻 | `revocation_state = none` |
| REJECT | 同上 | 同上 | 同上 | — | REJECT の時刻 | `life_reject.reason`、`counter_offer` |
| REVERSE | 同上 | 同上 | — | `grant` | REVERSE の時刻 | `payload.reason`、`grant.state`、`deletions[]` |
| 開示 | 要求が参照する ID | `grant` の相手 | — | `grant.agreed` | 開示の時刻 | 実際に開示した層・段階・項目 |
| 提案の受領 | 同上 | 同上 | — | — | 受領の時刻 | — |
| ゲート拒否 | 同上 | 要求者 | — | `grant` | 拒否の時刻 | 拒否したチェック ID |
| 削除状態の変化 | 同上 | 同上 | — | — | 変化の時刻 | `deletion.status`、`assertion_source` |

L3 の内容は外部に開示しない（LCS の上限 D0）。

---

# 11. 対応表と検証ケース

## 11.1 要求の対応表

依頼 4 章の各要求が、Core のどのフィールド・フェーズ、またはどの拡張で満たされるか。

| 要求 | 満たす手段 | 区分 |
|---|---|---|
| 4.1 身元 | `agent.id` / `agent.provider`、署名（`signed_fields`）、任意で `trust.evidence` | Core |
| 4.1 目的 | `declaration.purpose` | 拡張 |
| 4.1 求める層 | `declaration.requested_disclosure[].layer` | 拡張 |
| 4.1 開示段階 | `declaration.requested_disclosure[].stage` / `.items[]` | 拡張 |
| 4.1 介入レベル | `declaration.requested_intervention_level` + `intent` / `decision_authority` の整合（4.3） | 拡張 + Core の制約 |
| 4.1 保持期間 | `declaration.retention` | 拡張 |
| 4.1 二次利用 | `declaration.secondary_use`、`purpose_limitation_pledge` | 拡張 |
| 4.1 宣言の欠落で拒否 | O-1、REJECT `declaration_missing` | 拡張（Core の REJECT） |
| 4.2 既定値 | 6.2 ［提案］ | プロファイル |
| 4.2 上限・既定値・合意値の区別 | 6.1、`grant.agreed` | プロファイル |
| 4.2 実効値の算出 | 6.3、O-4、O-5、G-4 | プロファイル |
| 4.2 D1 も開示 | 6.4 | プロファイル |
| 4.3 HELLO | Core の HELLO + H-1〜H-3 | Core + プロファイルのチェック |
| 4.3 OFFER | Core の OFFER + `life_profile.declaration` + O-1〜O-10 | Core + 拡張 |
| 4.3 ACCEPT（狭めて受諾） | REJECT + `counter_offer` → 新しいハンドシェイクで再 OFFER → ACCEPT（5.4） | Core のまま（変更提案 CP-1） |
| 4.3 REJECT | Core の REJECT + `life_reject` | Core + 拡張 |
| 4.3 REVERSE | `authority_revoked` + `payload.reason` の理由コード | Core |
| 4.3 保留 | REJECT `consent_on_hold` または ACCEPT を返さない | Core のまま（変更提案 CP-2） |
| 4.4 即時停止 | `grant.state` の即時反映 + G-1 | プロファイル |
| 4.4 過去の ACCEPT が残らない | 7 章のゲート | プロファイル |
| 4.4 委譲の期限切れ | `delegation.expires_at`、`grant.valid_until`、G-2 | 拡張 |
| 4.4 authority_revoked → AI→Human | Core の REVERSE 必須チェック | Core |
| 4.5 宣言と履行の区別 | `assertion_source` | 拡張 |
| 4.5 削除状態の区別 | `deletion.status` | 拡張 |
| 4.6 L3 への記録 | `life_record`、10 章 | 拡張 |

## 11.2 用語の読み替え

| LVC の用語 | CCP 上の表現 | 注記 |
|---|---|---|
| 本人 | `decision_authority` の Human | CCP の participant ではない |
| 本人側エージェント | `participants.receiver` | |
| 外部 AI | `participants.initiator` | |
| 上限 | （CCP に無い。LCS を参照） | |
| 既定値 | 本プロファイル 6.2 | |
| 合意値 | ACCEPT された `life_profile.declaration` = `grant.agreed` | |
| 停止・取消・終結 | REVERSE `authority_revoked` + 理由コード | |
| 保持期間 | `declaration.retention` | `handshake_meta.expires_at` とは別物 |
| 接続の期限 | `declaration.connection_valid_until` | 同上 |

## 11.3 検証ケース

### ケース 1：外部 AI が資産情報を参照し、リバランスを提案する

前提：本人は目的 `finance.rebalance_proposal` を許可、L0 の資産項目に個別の同意は無い（既定値 案 A：L0 = D2）、IB 設定はレベル 3。

| 手順 | メッセージ | チェック | 結果 |
|---|---|---|---|
| 1 | HELLO（`world.id = lvc.life`） | Core HELLO、H-1〜H-3 | 通過 |
| 2 | OFFER：L0 = D3、レベル 3、`retention = session`、二次利用なし | O-4 通過（上限 D3）、O-5 不合格（既定値 D2 を超え、本人の同意なし） | REJECT `exceeds_person_consent`、`counter_offer`：L0 = D2 |
| 3 | 新しい HELLO / OFFER：L0 = D2、`previous_handshake_id` あり | O-1〜O-10 | 通過 |
| 4 | ACCEPT | Core ACCEPT | `grant.state = active`、L3 に記録 |
| 5 | 外部 AI が残高推移を問い合わせる | G-1〜G-6 → LCS → IB | D2 で開示、提案を受領、L3 に記録 |
| 6 | 本人が取消 | `grant.state = revoked`（即時） | REVERSE `authority_revoked` / `person_revoke` + 削除要求（`requested`） |
| 7 | 外部 AI が再度問い合わせる | G-1 不合格 | 拒否、`gate_denied` を記録 |
| 8 | 外部 AI が削除完了を宣言 | — | `deletion.status = declared_complete`（`verified` ではない） |

### ケース 2：本人が停止を宣言した後、外部 AI が以前の権限で実行を試みる

| 手順 | メッセージ | チェック | 結果 |
|---|---|---|---|
| 1 | （以前の ACCEPT で `grant.state = active`、レベル 4） | — | — |
| 2 | 本人が停止 | `grant.state = stopped`（即時、REVERSE の到達を待たない） | REVERSE `person_stop` |
| 3 | 外部 AI が以前の `handshake_id` で実行を要求 | G-1 不合格 | 拒否。LCS / IB には渡らない。`gate_denied` を記録 |
| 4 | REVERSE が外部 AI に届かなかった場合 | 同上 | 結果は同じ（判定は本人側で閉じる） |

### 「動かないこと」の確認

| 状況 | 期待する結果 | 満たす手段 |
|---|---|---|
| 本人が接続を許可しない | 外部 AI へデータが渡らない | H-2 で REJECT `connection_not_permitted`。ACCEPT が無いため `grant` が無く、G-1 で全要求を拒否 |
| 上限を超えた開示要求 | 上限内に縮小、または拒否 | O-4 で REJECT + `counter_offer`（上限内）、または縮小案なしの REJECT。ACCEPT 後の要求は G-4 で拒否 |
| 委譲の期限切れ | 権限が失効する | `grant.valid_until` ≤ `delegation.expires_at`、G-2 で拒否、REVERSE `delegation_expired` |
| 本人が停止を宣言 | 新規の実行を遮断 | `grant.state = stopped`、G-1 |
| 停止直前に取得した実行許可 | 実行直前の再確認で拒否 | 7 章：要求のたびに G-1 を評価。さらに IB が実行直前に停止状態を確認 |
| REVERSE を実行 | 新規の開示を止め、外部での削除の状態を区別する | `grant.state` の即時反映 + G-1、`deletion.status`（requested / declared_complete / verified / no_response） |

---

# 12. Core への変更提案

本プロファイルは、Core を変更せずにすべての要求を満たす（回避策を含む）。ただし次の点は、Core を変えた方が明快になるため、提案として分けて示す。本プロファイルの適用には必須ではない。

| ID | 提案 | 理由 | 現在の回避策 |
|---|---|---|---|
| CP-1 | ACCEPT 時の縮小、または COUNTER 状態の追加 | Core の ACCEPT は「そのまま承認」のみ。狭めて受諾するたびに新しいハンドシェイクが必要になり、往復が増え、一続きの交渉が Core 上は別々のハンドシェイクになる | REJECT + `counter_offer` → 新しいハンドシェイクで再 OFFER（`previous_handshake_id` で連結） |
| CP-2 | 保留（PENDING）状態の追加 | 「選択できない状況」で受諾を確定させずに保留したいが、Core には ACCEPT / REJECT 以外の応答が無い | REJECT `consent_on_hold`、または ACCEPT を返さず `expires_at` 切れ |
| CP-3 | ACCEPT 後の接続の有効期間と、ACCEPT 後の REVERSE の位置づけの明記 | Core の Termination は「ACCEPT の署名検証に成功した時点で成功」とし、接続が続く期間を定めていない。REVERSE は状態遷移上 ACCEPT の後に置かれているが、ACCEPT 後の扱いが明記されていない | `connection_valid_until` と `grant` を拡張で定義 |
| CP-4 | `reversal_signal.events[].type` の細分化（停止・取消・終結・削除要求） | 現在は `authority_revoked` と `payload.reason` の組で表している | `payload.reason` に理由コードを入れる |

参考（Core の不整合の観測。変更はしていない）：`specs/handshake.yaml` の `meta.version` は `2.1` だが、同ファイル内の `schema_definition.version` は `2.0` のままである。

---

# 13. 未決事項（LVC 側と相談が必要なもの）

| ID | 事項 |
|---|---|
| U-1 | 具体的な既定値（6.2 の開示段階、保持期間、接続の有効期限）。案 A を原案として提示 |
| U-2 | 削除完了の検証方法（LVC と共通の未決事項）と、`no_response` とみなす期限 |
| U-3 | 目的（`purpose.id`）の分類体系と、本人の許可との一致の判定方法 |
| U-4 | `world.id` の値（`"lvc.life"` は提案） |
| U-5 | 「選択できない状況」を検知し PSA に保留を伝える IB 側のインタフェース |
| U-6 | 項目単位の許可を表す項目 ID の体系（LCS 側） |
| U-7 | 本人の許可（目的・層・段階・保持期間・接続期間）を PSA が LCS / IB から受け取る形式 |
| U-8 | L3 の記録形式と、本書の `life_record` のフィールド名の対応 |
| U-9 | `stopped` から `active` への再開を認めるか（本書は新しいハンドシェイクを提案） |
| U-10 | 外部 AI の身元の検証強度（`trust.evidence` を必須にするか、`attested` を求めるか） |
| U-11 | 外部 AI が第三者へ再提供する場合（onward transfer）の扱い。本書では二次利用の一区分とし、宣言された場合は REJECT を提案 |
| U-12 | 介入レベル 5 の委任を CCP の `Human→AI` 遷移で表すことの是非（DA-3） |

---

# 14. LVC 側への申し送り

本プロファイルの作成にあたり LVC の文書は編集していない。LVC 側で検討が必要と考えた点を記す。

1. 依頼時に Core 上の対応候補とされた `interface.input` / `trust.scope`（求める層）と `decision_authority`（介入レベル）は、Core 上の意味が異なるため層・介入レベルの表現には採用せず、拡張フィールドとした（4.1）。LVC の文書がこれらの対応を前提にしている場合は、本書の対応表（11.1）に合わせた更新を検討してほしい。
2. L3 の記録形式に、`handshake_id` / `previous_handshake_id`、宣言のハッシュ、`assertion_source`、削除状態（`requested` / `declared_complete` / `verified` / `no_response`）を受け取れる欄があることが望ましい（10 章）。
3. IB 6 章の「保留」を PSA に伝えるインタフェースが必要である（5.5、U-5）。
4. 接続の有効期限（`connection_valid_until`）は本プロファイルで新たに導入した概念である。LVC の「委譲の期限」との関係（同一か、別に持つか）を確認してほしい。

---

# 付録 A. LVC 側の定義の抜粋（参照のみ）

本付録は LVC の定義を参照用に写したものであり、正本は LVC リポジトリにある。本書はこれらの意味を変えない。

**LCS の層**：L0 事実 / L1 価値 / L2 判断 / L3 接続・委譲（外部には開示しない）

**LCS の開示段階**：D0 非開示 / D1 存在のみ / D2 抽象化（手元で抽象化）/ D3 要約（本人が確認した要約）/ D4 原文

**LCS の上限**：L0 = D3 / L1 = D2 / L2 = D1 / L3 = D0

**IB の介入レベル**（既定値はレベル 2、引き上げは本人の操作だけ）：0 不関与 / 1 観測 / 2 提示 / 3 提案 / 4 確認付き実行 / 5 委任実行

**IB の起動条件**：要求時 / 許可イベント / 自発（既定では自発を禁止）

---

# License

MIT License
© VCDesign Project
