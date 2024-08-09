package lila.app

import scala.concurrent.{ ExecutionContext, Future }

import reactivemongo.api.*
import lila.i18n.I18nKeys.database
import reactivemongo.api.bson.{
  BSONDocumentWriter,
  BSONDocumentReader,
  Macros,
  document,
  BSONString,
  BSONDocument,
  BSONArray
}
import lila.db.dsl.{ *, given }
import lila.Lila.some
import reactivemongo.api.{ FailoverStrategy, ReadPreference }
import reactivemongo.api.commands.{ CommandWithPack, CommandWithResult, Command }
import reactivemongo.api.FailoverStrategy
import reactivemongo.api.commands.Command

import reactivemongo.api.bson.BSONDocument
import reactivemongo.api.bson.collection.BSONSerializationPack

object Hello:
  import ExecutionContext.Implicits.global // use any appropriate context

  def main(args: Array[String]) =
    val mongoDriver     = AsyncDriver()
    val parsedURIFuture = MongoConnection.fromString("mongodb://127.0.0.1:27017?appName=lila")
    val connection      = parsedURIFuture flatMap { parsedUri => mongoDriver.connect(parsedUri) }
    val db              = connection flatMap { conn => conn database "lichess" }
    val col             = db map { _.collection("puzzle2_round") }

    // // ###################################################
    // val result = col.flatMap(c => c.find(document()).cursor().collect(3))
    // val y = result map { value =>
    //     // val q = value(0).get("_id") match {
    //     //     case Some(bsonString: BSONString) => Some(bsonString.value)
    //     //     case _ => None
    //     // } getOrElse "No value"
    //     println(s"The result is: ${BSONDocument.pretty(value(0))}")
    // }

    // // ###################################################
    // val result2 = col
    //   .flatMap:
    //     _.aggregateOne(): framework =>
    //       import framework.*
    //       Match(document()) -> List(
    //         Project(
    //           $doc(
    //             "puzzle_id" ->
    //               $doc(
    //                 "$arrayElemAt" -> $arr(
    //                   $doc("$split" -> $arr("$_id", ":")),
    //                   1
    //                 )
    //               ),
    //             "u" -> 1,
    //             "w" -> 1
    //           )
    //         ),
    //         Group("puzzle_id")(
    //                 // "_id" -> "$puzzle_id"
    //             // "count" -> $doc("$count" -> $doc())
    //             "count" -> SumField("u")
    //         )
    //       )
    //   .map: docOpt =>
    //     docOpt
    // val y2 = result2 map: value =>
    //   println(BSONDocument.pretty(value getOrElse BSONDocument("msg" -> "no")))

    // val commandDoc = $doc(
    //     "aggregate" -> "puzzle2_round",
    //     "pipeline" -> $arr(
    //         $doc(f"$$project" -> $doc("u" -> 1, "w" -> 1)),
    //         $doc(f"$$limit" -> 1)
    //     )
    // )
    // println(BSONDocument.pretty(commandDoc))

    // val commandDoc = BSONDocument(
    //   "aggregate" -> "orders", // we aggregate on collection `orders`
    //   "pipeline" -> BSONArray(
    //     BSONDocument(f"$$match" -> BSONDocument("status" -> "A")),
    //     BSONDocument(
    //       f"$$group" -> BSONDocument(
    //         "_id" -> f"$$cust_id",
    //         "total" -> BSONDocument(f"$$sum" -> f"$$amount"))),
    //     BSONDocument(f"$$sort" -> BSONDocument("total" -> -1))
    //   )
    // ) // For example, otherwise rather use `.aggregatorContext` with a collection

    // val result = db.flatMap(_.runCommand(commandDoc, FailoverStrategy.default).
    //   cursor[BSONDocument](ReadPreference.primaryPreferred).head)
    // val y = result map: value =>
    //   println(BSONDocument.pretty(value(0)))









    // val user = "test"
    // val commandDoc = $doc(
    //   "aggregate" -> "puzzle2_round",
    //   "pipeline" -> $arr(
    //     $doc(
    //       "$project" -> $doc(
    //         "puzzle_id" ->
    //           $doc(
    //             "$arrayElemAt" -> $arr(
    //               $doc("$split" -> $arr("$_id", ":")),
    //               1
    //             )
    //           ),
    //         "u" -> 1,
    //         "w" -> 1
    //       )
    //     ),
    //     $doc(
    //       "$group" -> $doc(
    //         "_id"          -> "$puzzle_id",
    //         "count"        -> $doc("$count" -> $doc()),
    //         "done_by_user" -> $doc("$sum" -> $doc("$cond" -> $arr($doc("$eq" -> $arr("$u", f"$user")), 1, 0)))
    //       )
    //     ),
    //     $doc(
    //       "$match" -> $doc(
    //         "done_by_user" -> 0
    //       )
    //     ),
    //     $doc(
    //       "$sort" -> $doc(
    //         "count" -> 1
    //       )
    //     ),
    //     $doc("$limit" -> 1),
    //     $doc(
    //       "$unionWith" -> $doc(
    //         "coll" -> "puzzle2_puzzle",
    //         "pipeline" -> $arr(
    //           $doc("$sample" -> $doc("size" -> 1)),
    //         )
    //       )
    //     ),
    //     $doc("$limit" -> 1),
    //     $doc(
    //       "$addFields" -> $doc(
    //         "puzzleId" -> "$_id",
    //         // "roundId" -> $doc("$concat" -> $arr(s"$user${PuzzleRound.idSep}", "$_id"))
    //         "roundId" -> $doc("$concat" -> $arr(s"${user}:", "$_id"))
    //       )
    //     ),
    //     $doc(
    //       "$lookup" -> $doc(
    //         // "from"         -> colls.puzzle.name.value,
    //         "from"         -> "puzzle2_puzzle",
    //         "localField"   -> "puzzleId",
    //         "foreignField" -> "_id",
    //         "as"           -> "puzzle"
    //       )
    //     ),
    //     $doc(
    //       "$lookup" -> $doc(
    //         // "from"         -> colls.round.name.value,
    //         "from"         -> "puzzle2_round",
    //         "localField"   -> "roundId",
    //         "foreignField" -> "_id",
    //         "as"           -> "round"
    //       )
    //     )
    //   ),
    //   "cursor" -> BSONDocument()
    // )
    // val result3 = db.flatMap(
    //   _.runCommand(commandDoc, FailoverStrategy.default)
    //     .cursor[BSONDocument](ReadPreference.primaryPreferred)
    //     .collect(1)
    // )
    // val y3 = result3 map: value =>
    //   println(BSONDocument.pretty(value(0)))


    val user = "test"
    val commandDoc = $doc(
      "aggregate" -> "puzzle2_round",
      "pipeline" -> $arr(
        $doc(
          "$project" -> $doc(
            "puzzle_id" ->
              $doc(
                "$arrayElemAt" -> $arr(
                  $doc("$split" -> $arr("$_id", ":")),
                  1
                )
              ),
            "u" -> 1,
            "w" -> 1
          )
        ),
        $doc(
          "$group" -> $doc(
            "_id"          -> "$puzzle_id",
            "count"        -> $doc("$count" -> $doc()),
            "done_by_user" -> $doc("$sum" -> $doc("$cond" -> $arr($doc("$eq" -> $arr("$u", f"$user")), 1, 0)))
          )
        ),
        $doc(
          "$unionWith" -> $doc(
            "coll" -> "puzzle2_puzzle",
            "pipeline" -> $arr(
              $doc("$addFields" -> $doc(
                "count" -> 0,
                "done_by_user" -> 0
                )
              ),
            )
          )
        ),
        $doc(
          "$sort" -> $doc(
            "count" -> 1
          )
        ),
        $doc(
          "$group" -> $doc(
            "_id" -> "$_id",
            "count" -> $doc("$last" -> "$count"),
            "done_by_user" -> $doc("$last" -> "$done_by_user")
          )
        ),
        $doc(
          "$match" -> $doc(
            "done_by_user" -> 0
          )
        ),
        $doc(
          "$sort" -> $doc(
            "count" -> 1
          )
        ),
        $doc("$limit" -> 1),
        $doc(
          "$addFields" -> $doc(
            "puzzleId" -> "$_id",
            // "roundId" -> $doc("$concat" -> $arr(s"$user${PuzzleRound.idSep}", "$_id"))
            "roundId" -> $doc("$concat" -> $arr(s"${user}:", "$_id"))
          )
        ),
        $doc(
          "$lookup" -> $doc(
            // "from"         -> colls.puzzle.name.value,
            "from"         -> "puzzle2_puzzle",
            "localField"   -> "puzzleId",
            "foreignField" -> "_id",
            "as"           -> "puzzle"
          )
        ),
        $doc(
          "$lookup" -> $doc(
            // "from"         -> colls.round.name.value,
            "from"         -> "puzzle2_round",
            "localField"   -> "roundId",
            "foreignField" -> "_id",
            "as"           -> "round"
          )
        )
      ),
      "cursor" -> BSONDocument()
    )
    val result3 = db.flatMap(
      _.runCommand(commandDoc, FailoverStrategy.default)
        .cursor[BSONDocument](ReadPreference.primaryPreferred)
        .collect(1)
    )
    val y3 = result3 map: value =>
      println("++++++++++++++++++++++++++++++++++++++++++++++++")
      println(BSONDocument.pretty(value(0)))
