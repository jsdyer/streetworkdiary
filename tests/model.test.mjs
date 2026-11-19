import { test } from "node:test";
import assert from "node:assert/strict";
import { counts } from "../web/model.mjs";
test("closures, details and elapsed days use independent fields", () => {
  const rows = [
    [1, "A", "B", "D", "OPEN", null, false, ["a"], false],
    [2, "A", "B", "D", "CLOSED", 0, true, [], false],
    [3, "A", "B", "D", "CLOSED", null, false, [], false],
  ];
  assert.deepEqual(counts(rows), {
    total: 3,
    closed: 2,
    detail: 1,
    resolution: 1,
    elapsed: 0,
  });
});
