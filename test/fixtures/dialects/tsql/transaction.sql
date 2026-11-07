BEGIN TRANSACTION;
DELETE FROM HumanResources.JobCandidate
    WHERE JobCandidateID = 13;
COMMIT;

BEGIN TRAN;
DELETE FROM HumanResources.JobCandidate
  WHERE JobCandidateID = 13;
ROLLBACK TRAN;

BEGIN TRAN;
SAVE TRANSACTION;

BEGIN TRAN namey;
ROLLBACK namey;
SAVE TRAN @variable;
COMMIT @variable;
BEGIN TRANSACTION CandidateDelete WITH MARK N'Deleting a Job Candidate';
COMMIT TRANSACTION CandidateDelete;
BEGIN TRAN marked WITH MARK;
COMMIT;
