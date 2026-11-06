export const EDIT_WINDOW_MINUTES = 15;

export function isWithinEditWindow(
  createdAt: string,
  recordedBySchoolId: string | undefined,
  userSchoolId: string | undefined,
  canOverride: boolean,
  now: number = Date.now(),
): boolean {
  if (canOverride) return true;
  if (!userSchoolId || !recordedBySchoolId || recordedBySchoolId !== userSchoolId) return false;
  const created = Date.parse(createdAt);
  return Number.isFinite(created) && now - created <= EDIT_WINDOW_MINUTES * 60_000;
}
