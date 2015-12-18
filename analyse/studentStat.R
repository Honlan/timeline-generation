labels <- read.table("../data/action.txt", sep='^');
colnames(labels) <- c("id","stu_id","news_id","tag","timestamp");
labels$id <- as.factor(labels$id)
labels$stu_id <- as.factor(labels$stu_id)
labels$news_id <- as.factor(labels$news_id)
labels$tag <- as.factor(labels$tag)