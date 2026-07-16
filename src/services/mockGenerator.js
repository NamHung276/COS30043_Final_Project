export function generateMockModerationData(users, posts, reviewsCount) {
  const reports = [];
  const activities = [];

  const getRandomElement = (arr) => {
    if (!arr || arr.length === 0) return null;
    return arr[Math.floor(Math.random() * arr.length)];
  };

  const getRandomInt = (min, max) => {
    return Math.floor(Math.random() * (max - min + 1)) + min;
  };

  const reportReasons = {
    Review: ["Spam Bot Activity", "Offensive Language", "Irrelevant Content", "Troll Review"],
    Article: ["Duplicate Article Submission", "Misleading Title", "Plagiarism", "Low Effort Content"],
    Player: ["Offensive Username", "Harassing Behavior", "Suspected Bot Account", "Profile Image Violation"],
    Metadata: ["Misleading Game Information", "Incorrect Tags", "Broken Links", "Outdated Release Date"]
  };
  
  const severities = ["High", "Medium", "Low"];
  
  // Generate 4-7 random reports
  const numReports = getRandomInt(4, 7);
  for (let i = 0; i < numReports; i++) {
    const type = getRandomElement(["Review", "Article", "Player", "Metadata"]);
    const reason = getRandomElement(reportReasons[type]);
    const severity = getRandomElement(severities);
    
    // Randomize times between 1 minute ago and 23 hours ago
    const timeVal = getRandomInt(1, 59);
    const timeType = getRandomElement(["m", "h"]);
    const time = `${timeVal}${timeType} ago`;
    
    let target = "Unknown Target";
    let user = "System";
    let icon = "🎮";
    
    // Bind to real data if possible
    if (type === "Article" && posts && posts.length > 0) {
      target = getRandomElement(posts).title;
      icon = "📰";
    } else if (type === "Player" && users && users.length > 0) {
      target = getRandomElement(users).displayName || getRandomElement(users).email || "Unknown Player";
      icon = "👤";
    } else if (type === "Review") {
      target = getRandomElement(["Cyberpunk 2077", "Elden Ring", "Starfield", "Baldur's Gate 3", "Apex Legends"]);
      icon = "⭐";
    } else {
      target = getRandomElement(["System Database", "Tag Directory", "Genre List", "Homepage Banner Config"]);
      icon = "🎮";
    }
    
    if (users && users.length > 0) {
      user = getRandomElement(users).displayName || getRandomElement(users).email || "Community Member";
    }
    
    reports.push({
      id: Date.now() + i,
      type,
      icon,
      target,
      user,
      reason,
      severity,
      time
    });
  }

  // Generate 5-8 random activities
  const numActivities = getRandomInt(5, 8);
  for (let i = 0; i < numActivities; i++) {
    const actTypes = ["delete", "approve", "promote", "signup"];
    const type = getRandomElement(actTypes);
    
    const timeVal = getRandomInt(1, 24);
    const time = `${timeVal} hour${timeVal > 1 ? 's' : ''} ago`;
    
    let action = "";
    
    if (type === "delete") {
      action = getRandomElement(["Deleted offensive review", "Removed duplicate article", "Banned suspected bot"]);
    } else if (type === "approve") {
      let postTitle = posts && posts.length > 0 ? getRandomElement(posts).title : "New Community Article";
      action = `Approved article: '${postTitle.substring(0,30)}${postTitle.length > 30 ? '...' : ''}'`;
    } else if (type === "promote") {
      let uName = users && users.length > 0 ? (getRandomElement(users).displayName || "Dedicated Player") : "Member";
      action = `${uName} promoted to Moderator`;
    } else if (type === "signup") {
      action = "New player account registered";
    }
    
    activities.push({
      id: Date.now() + 1000 + i,
      action,
      time,
      type
    });
  }

  // Sort reports by severity (High -> Medium -> Low)
  const sevMap = { "High": 3, "Medium": 2, "Low": 1 };
  reports.sort((a, b) => sevMap[b.severity] - sevMap[a.severity]);

  return { reports, activities };
}
